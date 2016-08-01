import logging
from flask import render_template, abort, request
from pprint import pprint
from sqlalchemy.sql import func
from sqlalchemy import or_, and_, exists
from geoalchemy2.elements import WKTElement
from datetime import datetime

from coastal import api
from coastal.database.database import db_session
from coastal.models import (Site, DataValue, Parameter, PointMeasurement,
                            Deployment, Geography)
import wdft


logging.basicConfig(level=logging.DEBUG)

# from coastal.assets import coastal_assets


main_blueprint = wdft.WDFTBlueprint(
            'coastal', __name__,
            static_folder='../../static',
            template_folder="../../templates",
            url_prefix='/coastal',
            static_url_path='/static')


@main_blueprint.route("", methods=["GET"])
def index():
    """

    """
    # bays = Geography.query.filter_by(geotype="bay").all()
    estuaries = Geography.query.filter_by(geotype="estuary").order_by(
        func.ST_Y(func.ST_Centroid(Geography.the_geom)).desc()).all()
    return render_template("main/index.j2", estuaries=estuaries)


@main_blueprint.route("/sites/site-list", methods=["GET"])
def site_list_table():
    sites = Site.query.filter(exists().where(DataValue.site_id == Site.id)).all()
    
    sites = [s.toJSON() for s in sites]
    # TODO: this should never be done, but I am doing it. Need to find a way to do this in one query, 
    # NOT in a loop...
    for s in sites:
        drange = db_session.query(func.min(DataValue.datetime_utc).label("min_date"), func.max(DataValue.datetime_utc).label("max_date"))\
                .filter(DataValue.site_id == s["id"])\
                .filter(DataValue.is_spotcheck == False)\
                .one()
        s["min_date"] = drange[0]
        s["max_date"] = drange[1]
    
    return render_template("main/site_list.j2", site_list=sites)


@main_blueprint.route("/sites/<site_code>", methods=["GET"])
def site_view(site_code):
    site = Site.query.filter_by(site_code=site_code).first()
    if not site:
        return abort(404, "no site for this site code")

    parameter_mask = ['instrument_battery_voltage', 'water_specific_conductance',
                      'water_electrical_conductivity']
    bad_par_ids = db_session.query(Parameter.id)\
                    .filter(Parameter.code.in_(parameter_mask))\
                    .all()


    parameters = Parameter.query\
            .filter(~Parameter.id.in_(bad_par_ids))\
            .filter(exists()
                .where((DataValue.parameter_id == Parameter.id) & (DataValue.is_spotcheck == False) & (DataValue.site_id == site.id))
            ).all()
    site_date_range = db_session.query(func.min(DataValue.datetime_utc).label("min_date"),
                func.max(DataValue.datetime_utc).label("max_date"))\
                .filter(DataValue.site == site)\
                .filter(DataValue.is_spotcheck == False)\
                .filter(DataValue.invalid == False)\
                .one()
    dates = {"max_date": site_date_range[1], "min_date": site_date_range[0]}

    # pt = WKTElement('POINT({lon} {lat})'.format(lon=site.lon, lat=site.lat), srid=4326)
    # nearest_sites = Site.query.order_by(Site.the_geom.distance_box(pt)).limit(10).all()
    # pprint(nearest_sites)

    return render_template("main/site_view.j2", parameters=parameters, site=site, dates=dates)


@main_blueprint.route("/point-measurements", methods=["GET"])
def point_measurements():

    bad_par_ids = db_session.query(Parameter.id)\
                    .filter(Parameter.code.in_(['instrument_battery_voltage']))\
                    .all()

    parameters = Parameter.query\
            .filter(~Parameter.id.in_(bad_par_ids))\
            .filter(exists()
                .where((PointMeasurement.parameter_id == Parameter.id))
            ).all()
    estuaries = Geography.query.filter_by(geotype="estuary").order_by(
        func.ST_Y(func.ST_Centroid(Geography.the_geom)).desc()).all()
    return render_template("main/point_measurements.j2", parameters=parameters,
        estuaries=estuaries)

@main_blueprint.route("/about", methods=["GET"])
def about():
    return render_template("main/about.j2")






