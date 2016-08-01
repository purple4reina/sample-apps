import logging
from geoalchemy2.functions import ST_AsGeoJSON
from geojson import Feature, FeatureCollection
from flask import Blueprint, request, current_app, make_response, Response
from flask.ext.login import login_required, current_user
import json
from sqlalchemy import func, exists, text, select, and_, or_
from sqlalchemy.orm import aliased
from pprint import pprint
from datetime import datetime as dt, timedelta
from dateutil import parser, relativedelta
from pandas import DataFrame
import pandas
import pytz
import StringIO
from coastal.cache import cache
from coastal import api
from wdft.util.json_utils import json_response, make_error
from coastal.models import (User, DataValue, Parameter, PointMeasurement,
                            Geography, Site, Agency, AgencySite, Deployment,
                            QAQC_Region, CalibrationValue)
from coastal.database.database import engine, db_session
from coastal.database.redis_client import redis_client

logging.basicConfig(level=logging.DEBUG)

api_blueprint = Blueprint('coastal_api', __name__, static_folder='../../static',
                          template_folder="../../templates",
                          url_prefix='/coastal/api',
                          static_url_path='/static')


def make_full_path_key():
    """Make a key that includes GET parameters. Use with cache to set the key with
        any query params.
    """
    return request.full_path


@api_blueprint.route("/user", methods=["GET"])
@login_required
def test():
    u = User.query.filter_by(id=current_user.id).first()
    return json_response(u)


@api_blueprint.route("/geography/<geo_id>", methods=["GET"])
def get_geo_unit(geo_id):
    # can cache these responses, set a max_age of 1 hr secs
    gu = Geography.query.filter_by(id=geo_id).first()
    if not gu:
        return make_error(404, "No geography for this id")

    resp = json_response(gu)
    resp.cache_control.max_age = 3600
    return resp


@api_blueprint.route("/parameters")
def get_parameters():
    pars = Parameter.query.all()
    return json_response(pars)


@api_blueprint.route("/parameters/<int:parameter_id>")
def get_parameter(parameter_id):
    par = Parameter.query.get(parameter_id)
    if not par:
        return make_error(404, "No parameter for this id")

    return json_response(par)


@api_blueprint.route("/sites", methods=["GET"])
def get_site_metadata():
    geo_id = request.args.get("geo_id", None)
    bbox = request.args.get("bbox", None)
    all_sites = request.args.get("all_sites", False)
    agency_id = request.args.get("agency_id", None)
    output_format = request.args.get("output_format", "json")


    # this filters out only the Sites that have actual data, no need to get all the sites?
    q = Site.query
    if not all_sites:
        q = q.filter(exists().where(DataValue.site_id == Site.id))
    if geo_id:
        q = q.filter(func.ST_Contains(Geography.the_geom, Site.the_geom))\
             .filter(Geography.id == geo_id)
    if agency_id:
        q = q.join(AgencySite).filter(AgencySite.agency_id == agency_id)
    if bbox:
        bbox = json.loads(bbox)
        q = q.filter(func.ST_Contains(func.ST_MakeEnvelope(bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1], 4326), Site.the_geom))
    sites = q.all()

    print sites

    return json_response(sites)


@api_blueprint.route("/sites/<site_code>/qaqc/<parameter_code>", methods=["GET", "POST"])
@login_required
def get_post_qaqc(site_code, parameter_code):
    """
        Create / Update the qaqc regions for a site after uploading new data and performing QA. 
        This also invalidates all the data points that are in the bounding boxes that were 
        created. 
    """

    site = Site.query.filter_by(site_code=site_code).first()
    if not site:
        return make_error(404, "no site for this code")

    par = Parameter.query.filter_by(code=parameter_code).first()
    if not par:
        return make_error(404, "no par for this code")

    if request.method == "GET":
        regs = QAQC_Region.query\
                .filter(QAQC_Region.site == site)\
                .filter(QAQC_Region.parameter == par)\
                .all()
        return json_response(regs)
    elif request.method == "POST":
        payload = request.json

        qa_regs = []
        reg_ids = [reg.get("id") for reg in payload if reg.get("id") is not None]
        print reg_ids
        db_session.query(QAQC_Region)\
            .filter(~QAQC_Region.id.in_(reg_ids))\
            .filter(QAQC_Region.parameter == par)\
            .filter(QAQC_Region.site_id == site.id)\
            .delete(synchronize_session=False)

        for r in payload:
            r["extent"][0][0] = parser.parse(r["extent"][0][0])
            r["extent"][1][0] = parser.parse(r["extent"][1][0])
            # check to see if this one already exists
            if r.get("id"):
                qaqc = QAQC_Region.query.filter_by(id=r["id"]).first()
                if not qaqc:
                    return make_error(404, "There is no QAQC region for this id!")
                qaqc.extent = r["extent"]
                qaqc.reason = r["reason"]
            else:
                qaqc = QAQC_Region()
                qaqc.site = site
                qaqc.parameter = par
                qaqc.extent = r["extent"]
                qaqc.reason = r["reason"]
                db_session.add(qaqc)
            qaqc.last_modified_user_id = current_user.id
            qa_regs.append(qaqc)

        # now update the data values, setting them all to be valid for a second.
        # the invalid ones will be taken care of below
        DataValue.query\
            .filter(DataValue.parameter == par)\
            .filter(DataValue.site == site)\
            .filter(DataValue.invalid == True)\
            .update({"invalid": False})
        for reg in qa_regs:
            DataValue.query\
                .filter(DataValue.site == site)\
                .filter(DataValue.parameter == par)\
                .filter(DataValue.datetime_utc >= reg.extent[0][0])\
                .filter(DataValue.datetime_utc <= reg.extent[1][0])\
                .filter(DataValue.value >= reg.extent[0][1])\
                .filter(DataValue.value <= reg.extent[1][1])\
                .update({"invalid": True})

        Deployment.query\
            .filter(Deployment.site == site)\
            .update({"requires_qaqc": False})
        db_session.commit()

        # need to clear anything in redis as data has changed???
        # REDIS_KEY_PREFIX = current_app.config.get("CACHE_KEY_PREFIX")
        # redis_key = REDIS_KEY_PREFIX + "/coastal/api/sites/" + site_code + "*"
        # keys = redis_client.keys(redis_key)
        # if len(keys):
        #     redis_client.delete(*keys)

        regs = QAQC_Region.query\
                    .filter(QAQC_Region.site == site)\
                    .filter(QAQC_Region.parameter == par)\
                    .all()

        return json_response(regs)


@api_blueprint.route("/sites/<site_code>/qaqc/approve", methods=["POST"])
@login_required
def approve_qaqc(site_code):
    """
        Approve the QA/QC that was already done on the data for a given parameter
    """
    # clear out the redis cache for this data, as it will serve up the old stuff
    # if not
    site = Site.query.filter_by(site_code=site_code).first()
    if not site:
        return make_error(404, "No site for this code")

    Deployment.query\
        .filter(Deployment.site == site)\
        .update({"requires_qaqc": False, "qaqc_approved": True})

    db_session.commit()

    REDIS_KEY_PREFIX = current_app.config.get("CACHE_KEY_PREFIX")
    redis_key = REDIS_KEY_PREFIX + "/coastal/api/sites/" + site_code + "*"
    keys = redis_client.keys(redis_key)
    if len(keys):
        redis_client.delete(*keys)
    return json_response("ok")


@api_blueprint.route("/sites/<site_code>/parameters", methods=["GET"])
def parameters_for_site(site_code):
    """
        List all params for which there is data for a site
    """
    # pars = Parameter.query.join(DataValue)\
    #           .join(Site)\
    #           .filter(func.lower(Site.site_code) == func.lower(site_code))\
    #           .all()
    site = Site.query.filter_by(site_code=site_code).first()
    if not site:
        return make_error(404, "No site exists for this site code")

    pars = Parameter.query.filter(exists()
                .where((DataValue.parameter_id == Parameter.id) & (DataValue.is_spotcheck == False) & (DataValue.site_id == site.id) & (DataValue.invalid == False))
            ).all()
    return json_response(pars)


@api_blueprint.route("/sites/<site_code>/field-notes", methods=["GET"])
def get_field_notes(site_code):

    deployments = Deployment.query\
                    .join(Site)\
                    .filter(Site.site_code == site_code)\
                    .filter(Deployment.notes != None)\
                    .order_by(Deployment.deployment_datetime_utc)\
                    .all()

    out = [{"text": d.notes, "deployment_datetime_utc": d.deployment_datetime_utc} for d in deployments]
    return json_response(out)



@api_blueprint.route("/sites/<site_code>/data", methods=["GET"])
def get_all_site_data(site_code):
    """
        Returns all data by default as csv, binned daily by default

        ?output_format=csv || json
    """

    site = Site.query.filter_by(site_code=site_code).first()
    if not site:
        return make_error(404, "No site for this code")

    output_format = request.args.get("output_format", "csv")
    sql = """
        select datetime_utc::date, avg(dv.value) as value, par.code as parameter_code from coastal.datavalue as dv
        join coastal.parameter as par on dv.parameter_id = par.id
        join coastal.site on dv.site_id = coastal.site.id
        where site.site_code = %(site_code)s
        and invalid is false
        and is_spotcheck is false
        group by datetime_utc::date, par.code
    """

    df = pandas.read_sql(sql, engine, params={"site_code": site_code})
    df = df.pivot(index='datetime_utc', columns='parameter_code', values='value')

    io = StringIO.StringIO()
    df.to_csv(io, index=True)
    resp = make_response(io.getvalue())
    resp.headers["Content-Disposition"] = "attachment; filename={site_code}.csv".format(site_code=site.site_code)
    resp.headers["Content-type"] = "text/csv"
    return resp


@api_blueprint.route("/sites/<site_code>/data/<parameter_code>", methods=["GET"])
# @cache.cached(key_prefix=make_full_path_key, timeout=3600 * 24 * 30)
def get_timeseries_data(site_code, parameter_code):
    """
        Returns the timeseries data for a given site and parameter

        ?output_format=csv
        ?period=1m
        ?qaqc=true
        ?binning=month,day,hour,minute
    """

    # HERE BE DRAGONS...
    
    allowed_params = ("qaqc", "output_format", "start_date", "end_date", "period", "binning")
    for q in request.args:
        if q not in allowed_params:
            return make_error(422, "Invalid query parameter")
    qaqc = request.args.get("qaqc", False)
    output_format = request.args.get("output_format", "json")
    start_date = request.args.get("start_date", None)
    end_date = request.args.get("end_date", None)
    period = request.args.get("period", "1m")
    binning = request.args.get("binning", "day")

    if period not in ['1m', '6m', '1y', 'max']:
        return make_error(422, "periods of 1m, 6m, 1y, max are only allowed")
    
    if binning not in ['hour', 'min', 'day', 'mon']:
        return make_error(422, 'binning of hour, min, day allowed')

    central_tz = pytz.timezone('US/Central')
    if start_date:
        try:
            start_date = central_tz.localize(parser.parse(start_date))
        except ValueError:
            return make_error(422, "start_date format is YYYY-MM-DD")

    if end_date:
        try:
            end_date = central_tz.localize(parser.parse(end_date))
        except ValueError:
            return make_error(422, "end_date format is YYYY-MM-DD")

    site = Site.query.filter(func.lower(Site.site_code) == func.lower(site_code)).first()
    if not site:
        return make_error(404, "no site for this site code")
    
    parameter = Parameter.query.filter_by(code=parameter_code).first()
    if not parameter:
        return make_error(404, "no parameter for this code")

    if not qaqc:
        dep_alias = aliased(Deployment)

        q = db_session.query(
            func.avg(DataValue.value).label('value'),
            func.date_trunc(binning, DataValue.datetime_utc).label('datetime_utc')
        )

        q = q.outerjoin(dep_alias)\
            .filter(DataValue.site_id == site.id)\
            .filter(DataValue.parameter_id == parameter.id)\
            .filter(DataValue.is_spotcheck == False)\
            .filter(DataValue.invalid == False)\
            .filter(or_(dep_alias.requires_qaqc == False, dep_alias.requires_qaqc == None))\
            .filter(or_(dep_alias.qaqc_approved == True, dep_alias.qaqc_approved == None))

        if start_date:
            q = q.filter(DataValue.datetime_utc > start_date)

        if end_date:
            q = q.filter(DataValue.datetime_utc < end_date)

        q = q.group_by(func.date_trunc(binning, DataValue.datetime_utc))\
                .order_by(func.date_trunc(binning, DataValue.datetime_utc))
    else:
        q = db_session.query(
                DataValue.value,
                func.to_char(DataValue.datetime_utc, 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"').label('datetime_utc'),
                DataValue.deployment_id,
                DataValue.invalid
            )\
            .filter(DataValue.site_id == site.id)\
            .filter(DataValue.parameter_id == parameter.id)\
            .filter(DataValue.is_spotcheck == False)\
            .order_by(DataValue.datetime_utc)
    


    df = pandas.read_sql(q.statement, q.session.bind, index_col="datetime_utc")
    df["datetime_utc"] = df.index
    # df.dropna(inplace=True)
    #if csv is requested...
    if output_format == "csv":
        if site.agency.abbreviation.lower() != 'twdb':
            header = '# This site is owned/operated by %s and data is provided on this website as is. \n' % site.agency.name
        else:
            header = (
                '# This data has been collected by a Texas Water Development Board datasonde.\n'
                '# Raw data may contain errors. Provisional data has had anomalous \n'
                '# individual data points removed. Such data points typically are disconnected \n'
                '# from the recorded trend. Nonetheless all removed data is retained in database. \n'
                '# However data that simply appear unusual are not removed unless verifying \n'
                '# information is obtained suggesting the data is not representative of bay conditions. \n'
                '# The Board makes no warranties (including no warranties as to merchantability or fitness) either\n'
                '# expressed or implied with respect to the data or its fitness for any specific application.\n')
        header += '# Unit: %s \n' % parameter.units_name
            
        central_tz = pytz.timezone('US/Central')
        df.datetime_utc = df.index.tz_localize(pytz.utc).tz_convert(central_tz)
        df = df.rename(columns={"datetime_utc": "datetime"})
        df = df[["datetime", "value"]]
        io = StringIO.StringIO()
        io.write(header)
        df.to_csv(io, index=False, date_format='%Y-%m-%dT%H:%H:%S%z')
        resp = make_response(io.getvalue())
        resp.headers["Content-Disposition"] = "attachment; filename={site_code}_{parameter_code}.csv".format(site_code=site_code, parameter_code=parameter_code)
        resp.headers["Content-type"] = "text/csv"
        return resp

    return json_response(df)


@api_blueprint.route("/sites/<site_code>/<parameter_code>/spot-checks", methods=["GET"])
def get_spot_checks(site_code, parameter_code):
    site = Site.query.filter(func.lower(Site.site_code) == func.lower(site_code)).first()
    if not site:
        return make_error(404, "no site for this site code")
    parameter = Parameter.query.filter_by(code=parameter_code).first()
    if not parameter:
        return make_error(404, "no parameter for this code")
    vals = DataValue.query.filter(DataValue.site == site)\
            .filter(DataValue.parameter == parameter)\
            .filter(DataValue.is_spotcheck == True)\
            .all()
    return json_response(vals)


@api_blueprint.route("/sites/<site_code>/<parameter_code>/calibrations", methods=["GET"])
def get_calibrations(site_code, parameter_code):
    site = Site.query.filter(func.lower(Site.site_code) == func.lower(site_code)).first()
    if not site:
        return make_error(404, "no site for this site code")
    parameter = Parameter.query.filter_by(code=parameter_code).first()
    if not parameter:
        return make_error(404, "no parameter for this code")
    vals = CalibrationValue.query\
            .join(Deployment)\
            .filter(Deployment.site == site)\
            .all()
    return json_response(vals)


@api_blueprint.route('/geometries/<geometry_type>', methods=['GET'])
def get_geometries(geometry_type):
    if geometry_type not in ['bay', 'estuary', 'basin']:
        return make_error(404, 'no geometry for of this type')

    geometries = Geography.query.filter_by(geotype=geometry_type).all()
    features = []
    for geometry in geometries:
        geometry_str = db_session.scalar(ST_AsGeoJSON(geometry.the_geom))
        geometry_geojson = json.loads(geometry_str)
        feature = Feature(
            geometry=geometry_geojson, name=geometry.name,
            properties=geometry.extradata)
        features.append(feature)

    geometries_geojson = FeatureCollection(features)

    return json_response(geometries_geojson)


def _validate_bbox(bbox, max_area=1):

    min_lon = bbox[0][0]
    min_lat = bbox[0][1]
    max_lon = bbox[1][0]
    max_lat = bbox[1][1]

    bbox_area = (max_lon - min_lon) * (max_lat - min_lat)
    print bbox_area, bbox
    return bbox_area < max_area


@api_blueprint.route("/point-measurements/<parameter_code>", methods=["GET"])
def get_point_measurements(parameter_code):

    date = request.args.get("date")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    bbox = request.args.get("bbox")
    geo_id = request.args.get("geo_id")
    output_format = request.args.get("output_format", "json")

    if not any([date, start_date, end_date, bbox]):
        return make_error(400, "Must specify date, start_date + end_date, or bbox")

    if (start_date and not end_date) or (end_date and not start_date):
        return make_error(400, "Must specify both start_date and end_date")

    par = Parameter.query.filter_by(code=parameter_code).first()
    if not par:
        return make_error(404, "No parameter for this code exists!")

    q = db_session.query(
            func.to_char(PointMeasurement.datetime_utc, 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"').label("datetime_utc"),
            PointMeasurement.value.label("value"),
            func.ST_AsGeoJSON(PointMeasurement.the_geom).label("the_geom"),
            Parameter.code
        )\
        .join(Parameter)\
        .filter(PointMeasurement.parameter_id == par.id)\
        .filter(PointMeasurement.invalid == False)

    if date:
        q = q.filter(func.date(PointMeasurement.datetime_utc) == date)

    if start_date:
        q = q.filter(func.date(PointMeasurement.datetime_utc) >= start_date)

    if end_date:
        q = q.filter(func.date(PointMeasurement.datetime_utc) <= end_date)
    
    # should not be able to get all the data in one go, too much to handle in a
    # single request. Limit the grab to one month at a time
    if not bbox and (start_date and end_date):
        sd = parser.parse(start_date)
        ed = parser.parse(end_date)
        delta = ed - sd
        if delta.days > 31:
            return make_error(400, "Without a bounding box, a limit of 31 days of data is applied. Either use a bounding box or limit query to less than 31 days.")
    
    if bbox:
        try:
            bbox = json.loads(bbox)
        except:
            return make_error(400, "Invalid bounding box")

        bbox_valid = _validate_bbox(bbox, max_area=1)
        if not bbox_valid and not date:
            return make_error(400, "Bounding box too large, maximum of 1 square degree")

        q = q.filter(func.ST_Contains(func.ST_MakeEnvelope(bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1], 4326), PointMeasurement.the_geom))

    if geo_id:
        q = q.filter(func.ST_Contains(Geography.the_geom, PointMeasurement.the_geom))\
         .filter(Geography.id == geo_id)

    out = []
    for row in q:
        p = json.loads(row[2])
        coors = p["coordinates"]
        # flip them to be [x, y] NOT [y, x]
        # coors[0], coors[1] = coors[1], coors[0]
        d = dict(datetime_utc=row[0], value=row[1], coordinates=coors, parameter_code=row[3])
        out.append(d)
    
    if output_format == "csv":
        df = DataFrame(out)
        df.datetime_utc = pandas.to_datetime(df.datetime_utc)
        df.set_index("datetime_utc", inplace=True)
        df["lon"] = df.apply(lambda x: x.coordinates[0], axis=1)
        df["lat"] = df.apply(lambda x: x.coordinates[1], axis=1)
        del df["coordinates"]
        df.dropna(inplace=True)
        central_tz = pytz.timezone('US/Central')
        df.index = df.index.tz_localize(pytz.utc).tz_convert(central_tz)
        io = StringIO.StringIO()
        io.write("#units of {units}\n".format(units=par.units_name))
        io.write("#Spot measurements from Texas Parks and Wildlife Department's Coastal Fisheries Program. \n")
        df.to_csv(io, index=True)
        resp = make_response(io.getvalue())
        resp.headers["Content-Disposition"] = "attachment; filename=tpwd_cf_point_measurements_{date}.csv".format(date=date)
        resp.headers["Content-type"] = "text/csv"
        return resp
    else:
        return json_response(out)


def _no_cache_point_measurement():
    print "path", request.full_path.lower()
    if 'geo_id' not in request.full_path.lower():
        return True


@api_blueprint.route("/point-measurements/<parameter_code>/dates", methods=["GET"])
@cache.cached(key_prefix=make_full_path_key, timeout=86400*180, unless=_no_cache_point_measurement)
def get_point_measurements_dates(parameter_code):

    year = request.args.get("year", None)
    month = request.args.get("month", None)
    bbox = request.args.get("bbox", None)
    geo_id = request.args.get("geo_id", None)

    if bbox:
        bbox = json.loads(bbox)

    par = Parameter.query.filter_by(code=parameter_code).first()
    if not par:
        return make_error(404, "No parameter for this code exists!")

    if (not year) and (not month):
        out = api.point_measurement_years(par.code, bbox=bbox, geo_id=geo_id)
    elif year and not month:
        out = api.point_measurement_months(
            par.code, year, bbox=bbox, geo_id=geo_id)
    elif year and month:
        out = api.point_measurement_dates(
            par.code, year, month, bbox=bbox, geo_id=geo_id)

    return json_response(out)


@api_blueprint.route("/point-measurements/<parameter_code>/summary-statistics", methods=["GET"])
@cache.cached(key_prefix=make_full_path_key, timeout=86400*180, unless=_no_cache_point_measurement)
def point_measurement_summary(parameter_code):
    """?bbox=[[]]"""
    bbox = request.args.get("bbox")
    geo_id = request.args.get("geo_id", None)
    # q = db_session.query(
    #         func.extract('month', PointMeasurement.datetime_utc).label('mon'),
    #         func.extract('year', PointMeasurement.datetime_utc).label('year'),
    #         func.avg(PointMeasurement.value).label('mean'),
    #         # func.percentile_cont(0.5).within_group(PointMeasurement.value.desc()),
    #         func.stddev(PointMeasurement.value).label('stddev'),
    #         func.count(PointMeasurement.value).label('count')
    #     ).join(Parameter)\
    #     .filter(Parameter.code == parameter_code)\
    #     .group_by(func.extract('month', PointMeasurement.datetime_utc), func.extract('year', PointMeasurement.datetime_utc))\
    #     .order_by(func.extract('year', PointMeasurement.datetime_utc), func.extract('month', PointMeasurement.datetime_utc))
    select_statements = [
        text("coastal.point_measurement join coastal.parameter on coastal.point_measurement.parameter_id = coastal.parameter.id")]
    and_stmts = [
        text("coastal.parameter.code = :parameter_code"), text("coastal.point_measurement.invalid = false")
    ]
    # if bbox:
    #     bbox = json.loads(bbox)
    #     q = q.filter(func.ST_Contains(func.ST_MakeEnvelope(bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1], 4326), PointMeasurement.the_geom))
    if bbox:
        bbox = json.loads(bbox)
        bbox_stmt = text(" ST_Contains(ST_MakeEnvelope(:bbox_xmin, :bbox_ymin, :bbox_xmax, :bbox_ymax, 4326), the_geom)")
        and_stmts.append(bbox_stmt)

    if geo_id:
        select_statements.append(
            text("coastal.geograph"))
        and_stmts.append(text("coastal.geograph.id = :geo_id"))
        and_stmts.append("public.ST_contains(coastal.geograph.the_geom, coastal.point_measurement.the_geom)")

    s = select([text("extract('month' from datetime_utc) as mon"),
                text("extract('year'from  datetime_utc) as year"),
                text("(percentile_cont(0.50) within group (order by value)) as mean"),
                text("count(value) as count")])\
        .where(and_(*and_stmts))\
        .select_from(",".join([str(stmt) for stmt in select_statements]))\
        .group_by(text("extract('month' from datetime_utc), extract('year' from datetime_utc)"))\
        .order_by(text("extract('year'from datetime_utc), extract('month'from datetime_utc)"))

    if bbox:
        res = engine.execute(s, parameter_code=parameter_code,
                            bbox_xmin=bbox[0][0], bbox_ymin=bbox[0][1],
                            bbox_xmax=bbox[1][0], bbox_ymax=bbox[1][1])
    elif geo_id:
        res = engine.execute(s, parameter_code=parameter_code,
                             geo_id=geo_id)
    else:
        res = engine.execute(s, parameter_code=parameter_code)

    out = []
    for row in res:
        out.append(dict(zip(row.keys(), row)))

    return json_response(out)


@api_blueprint.route("/point-measurements/<parameter_code>/histogram", methods=["GET"])
@cache.cached(key_prefix=make_full_path_key, timeout=86400*180, unless=_no_cache_point_measurement)
def point_measurement_histogram(parameter_code):
    par = Parameter.query.filter_by(code=parameter_code).first()
    if not par:
        return make_error(404, "No parameter for this code.")
    bins = request.args.get("bins", 20)
    bbox = request.args.get('bbox')
    geo_id = request.args.get("geo_id")

    q1 = db_session.query(func.avg(PointMeasurement.value).label("avg"),
                          func.stddev(PointMeasurement.value).label("stddev")
                         ).join(Parameter)\
                         .filter(Parameter.code == par.code)\
                         .filter(PointMeasurement.invalid == False)

    if bbox:
        bbox = json.loads(bbox)
        q1 = q1.filter(func.ST_Contains(func.ST_MakeEnvelope(bbox[0][0], bbox[0][1],
                    bbox[0][1], bbox[1][1], 4326), PointMeasurement.the_geom))
    if geo_id:
        q1 = q1.filter(func.ST_Contains(Geography.the_geom, PointMeasurement.the_geom))\
                .filter(Geography.id == geo_id)

    global_stats = q1.first()
    avg, stddev = global_stats[0], global_stats[1]
    
    q2 = db_session.query(func.min(PointMeasurement.value), func.max(PointMeasurement.value))\
            .join(Parameter)\
            .filter(Parameter.code == par.code)\
            .filter(PointMeasurement.value < avg + 3 * stddev)\
            .filter(PointMeasurement.value > avg - 3 * stddev)

    if bbox:
        q2 = q2.filter(func.ST_Contains(func.ST_MakeEnvelope(bbox[0][0], bbox[0][1],
                    bbox[0][1], bbox[1][1], 4326), PointMeasurement.the_geom))
    if geo_id:
        q2 = q2.filter(func.ST_Contains(Geography.the_geom, PointMeasurement.the_geom))\
                .filter(Geography.id == geo_id)

    local_stats = q2.first()
    local_min, local_max = local_stats[0], local_stats[1]

    q3 = db_session.query(
            ((func.width_bucket(PointMeasurement.value, local_min, local_max, bins)- 1) * (local_max-local_min)/bins).label("bin"),
            func.count(PointMeasurement.value).label("freq")
        ).join(Parameter)\
        .filter(Parameter.code == par.code)\
        .filter(PointMeasurement.value < avg + 3 * stddev)\
        .filter(PointMeasurement.value > avg - 3 * stddev)\
        .group_by("bin")\
        .order_by("bin")

    if bbox:
        q3 = q3.filter(func.ST_Contains(func.ST_MakeEnvelope(bbox[0][0], bbox[0][1],
                    bbox[0][1], bbox[1][1], 4326), PointMeasurement.the_geom))
    if geo_id:
        q3 = q3.filter(func.ST_Contains(Geography.the_geom, PointMeasurement.the_geom))\
                .filter(Geography.id == geo_id)

    out = []
    for row in q3:
        out.append(dict(zip(row.keys(), row)))

    return json_response(out)
