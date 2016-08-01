import logging
from pprint import pprint
from datetime import datetime
from flask import (render_template, request, flash, redirect,
                   url_for, abort, session)
from flask.ext.login import login_required, login_user, logout_user, fresh_login_required
from flask.ext.uploads import UploadSet
from werkzeug import secure_filename
from dateutil import parser
from sqlalchemy import and_, func
import pytz

import wdft
from coastal.database.database import db_session, engine
from coastal.models.admin import User, Role
from coastal.models.site import Site
from coastal.models.deployment import Deployment
from coastal.models.calibration import CalibrationValue
from coastal.models.data import DataValue, Parameter
from coastal.models.instrument import Instrument, InstrumentParameter
from coastal.models.internal import Agency, Project, AgencyProject, AgencySite, ProjectSite
from coastal.util import sonde_utils
from coastal.util.decorators import requires_roles 
from data import load_utils

logging.basicConfig(level=logging.DEBUG)

from .forms import (LoginForm, PreDeploymentForm, DeploymentForm,
                    PostDeploymentForm, SiteForm, SiteEditForm,
                    UserCreateForm, UserEditForm, UserPasswordChangeForm,
                    SpotCheckEditForm, SpotCheckForm,
                    InstrumentForm, InstrumentEditForm,
                    GEOForm, AgencyForm, AgencyEditForm, 
                    CalibrationEditForm, CalibrationForm, PointMeasurementsUploadForm)


# rawdatafiles = UploadSet('rawdatafiles',
#             extensions=('txt', 'rtf', 'odf', 'ods', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'json', 'xml', 'dat',))

data_files = UploadSet('datafiles', ('csv', 'dat', 'xls', 'ysi'))

admin_blueprint = wdft.WDFTBlueprint(
    'coastal_admin', __name__, static_folder='../../static', template_folder="../../templates",
    url_prefix='/coastal/admin',
    static_url_path='/static'
)


@admin_blueprint.route("", methods=["GET"])
@login_required
def index():

    qaqc_sites = Site.query\
                     .join(Deployment)\
                     .filter(Deployment.requires_qaqc == True)\
                     .filter(Deployment.filename != None)\
                     .all()
    qaqc_approval_sites = Site.query\
                     .join(Deployment)\
                     .filter(Deployment.qaqc_approved == False)\
                     .filter(Deployment.filename != None)\
                     .all()
    print qaqc_approval_sites
    return render_template("admin/index.j2", qaqc_sites=qaqc_sites, qaqc_approval_sites=qaqc_approval_sites)


@admin_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out', 'success')
    return redirect(url_for('coastal_admin.login'))


@admin_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter(func.lower(User.email) == func.lower(form.email.data)).first()
        if not user:
            return render_template('admin/login.j2', form=form,
                                   auth_error=True)

        if user.check_password(form.password.data):
            login_user(user, remember=True)
            session.permanent = True
            user.date_last_login = datetime.utcnow()
            db_session.commit()

            # flash('You have logged in as %s' % user.username, 'success')

            # next will be set if the user was redirected to the login
            # page from a @login_required decorated function
            if 'next' in request.args:
                return redirect(request.args['next'])

            return redirect(url_for('coastal_admin.index'))

        else:
            return render_template('admin/login.j2', form=form,
                                   auth_error=True)

    return render_template('admin/login.j2', form=form, next=url_for('coastal_admin.index'))


@admin_blueprint.route('/sites', methods=['GET'])
@login_required
def site_list():
    sites = Site.query.order_by("site_code").all()
    # raise ValueError
    return render_template('admin/site_list.j2', sites=sites)


@admin_blueprint.route('/sites/create', methods=['GET', 'POST'])
@login_required
def site_create():
    form = SiteForm()
    agencies = Agency.query.all()
    form.agency_id.choices = [(a.id, a.name) for a in agencies]

    print form.validate()
    for field in form:
        print field.errors
    if request.method == 'POST' and form.validate():
        # make sure site does not already exist...
        site = Site()
        site.site_code = form.site_code.data
        site.description = form.description.data,
        site.set_geom(form.lon.data, form.lat.data)
        agency = Agency.query.filter_by(id=form.agency_id.data).first()
        site.agency = agency
        db_session.add(site)
        db_session.commit()
        return redirect(url_for('coastal_admin.site_list'))
    else:
        return render_template('admin/site.j2', 
                               form=form,
                               action=url_for('coastal_admin.site_create'),
                               title="Create Site")


@admin_blueprint.route('/sites/<site_code>/delete', methods=['POST'])
@requires_roles(["administrator"])
@login_required
def site_delete(site_code):
    site = Site.query.filter_by(site_code=site_code).first()
    if not site:
        return abort(404)

    sql = """ DELETE from coastal.site where id = %(site_id)s"""
    connection = engine.connect()
    result = connection.execute(sql, site_id=site.id)
    # db_session.delete(site)
    # db_session.commit()
    return redirect(url_for('coastal_admin.site_list'))


@admin_blueprint.route('/sites/<site_code>', methods=['GET', 'POST'])
@login_required
def site_edit(site_code):
    site = Site.query.filter_by(site_code=site_code).first()
    form = SiteEditForm(obj=site)
    agencies = Agency.query.all()
    form.agency_id.choices = [(a.id, a.name) for a in agencies]
    if not site:
        return abort(404)

    # preset the select dropdowns with the user data.
    if request.method == "GET":
        ag_site = AgencySite.query.filter_by(site_id=site.id).first()
        form.agency_id.data = ag_site.agency_id
    if request.method == 'POST' and form.validate():
        site.site_code = form.site_code.data
        site.description = form.description.data,
        site.set_geom(form.lon.data, form.lat.data)
        ag = Agency.query.filter_by(id=form.agency_id.data).first()
        site.agency = ag
        db_session.commit()
        return redirect(url_for('coastal_admin.site_list'))
    return render_template('admin/site.j2',
                           form=form,
                           action=url_for('coastal_admin.site_create'),
                           title="Edit Site")


@admin_blueprint.route('/sites/<site_code>/deployments/', methods=["GET"])
@login_required
def deployment_list(site_code):

    site = Site.query.filter_by(site_code=site_code).first()
    if not site:
        return abort(404)

    deploys = Deployment.query\
                .join(Site)\
                .filter(Site.site_code == site_code)\
                .order_by(Deployment.deployment_datetime_utc.desc()).all()
    return render_template("admin/deployment_list.j2", deploys=deploys, site=site)


@admin_blueprint.route('/deployments/<int:dep_id>/delete', methods=['POST'])
@requires_roles("administrator")
@login_required
def deployment_delete(dep_id):
    dep = Deployment.query.filter_by(id=dep_id).first()
    if not dep:
        return abort(404)
    db_session.delete(dep)
    db_session.commit()
    return redirect(url_for('coastal_admin.index'))


@admin_blueprint.route('/deployments/<site_code>/create', methods=["GET", "POST"])
@login_required
def deployment_create(site_code):
    site = Site.by_site_code(site_code)
    if not site:
        return abort(404)

    form = PreDeploymentForm()
    form.site.choices = [(s.id, s.site_code) for s in Site.query.all()]
    form.site.data = site.id
    ctd_instruments = Instrument.query.join(
        InstrumentParameter).filter(InstrumentParameter.parameter_id.in_([
            param.id for param in Parameter.get_ctd_parameters()])).all()
    do_instruments = Instrument.query.join(
        InstrumentParameter).filter(InstrumentParameter.parameter_id.in_([
            param.id for param in Parameter.get_ctd_parameters()])).all()

    form.ctd_ins_serial_number.choices = [(i.id, i.serial_number) for
                                          i in ctd_instruments]
    form.do_ins_serial_number.choices = [(i.id, i.serial_number) for
                                         i in do_instruments]

    if request.method == "GET":
        return render_template("admin/deployment.j2", predeploy_form=form, site=site)
    else:
        site_id = int(form.site.data)
        site = Site.query.filter_by(id=site_id).first()
        pprint(site)

        setup_datetime = parser.parse(form.setup_datetime.data)
        setup_datetime_utc = wdft.util.cst2utc_with_dst(setup_datetime)
        start_datetime = parser.parse(form.start_datetime.data)
        start_datetime_utc = wdft.util.cst2utc_with_dst(start_datetime)
        deployment = Deployment()
        deployment.site = site
        deployment.setup_datetime_utc = setup_datetime_utc
        deployment.start_datetime_utc = start_datetime_utc
        # form.populate_obj(deployment)
        ctd_ins_id = int(form.ctd_ins_serial_number.data)
        ctd_instrument = Instrument.query.filter_by(id=ctd_ins_id).first()
        deployment.instruments.append(ctd_instrument)
        if form.do_ins_serial_number.data:
            do_ins_id = int(form.do_ins_serial_number.data)
            do_instrument = Instrument.query.filter_by(id=do_ins_id).first()
            deployment.instruments.append(do_instrument)

        # deployment.filename = form.filename.data
        deployment.notes = form.notes.data
        deployment.setup_staff_name = form.setup_staff_name.data
        db_session.add(deployment)

        db_session.commit()
        flash('predeployment information uploaded', 'success')
        return redirect(url_for(
            '.deployment_edit', deployment_id=deployment.id))


@admin_blueprint.route('/deployments/<int:deployment_id>/<deploy_info>',
                       methods=["GET", "POST"])
@admin_blueprint.route('/deployments/<int:deployment_id>', defaults={'deploy_info': None},
                       methods=["GET", "POST"])
@login_required
def deployment_edit(deployment_id, deploy_info):
    deployment = Deployment.query.get(deployment_id)
    if deployment is None:
        abort(404)
    if not (deploy_info is None or deploy_info
            in ['predeploy', 'deploy', 'postdeploy']):
        abort(404)

    predeploy_form = PreDeploymentForm()
    predeploy_form.site.choices = [(s.id, s.site_code) for s in Site.query.all()]
    predeploy_form.site.data = deployment.site.id
    ctd_instruments = Instrument.query.join(
        InstrumentParameter).filter(InstrumentParameter.parameter_id.in_([
            param.id for param in Parameter.get_ctd_parameters()])).all()
    do_instruments = Instrument.query.join(
        InstrumentParameter).filter(InstrumentParameter.parameter_id.in_([
            param.id for param in Parameter.get_ctd_parameters()])).all()

    predeploy_form.ctd_ins_serial_number.choices = [(i.id, i.serial_number) for
                                                    i in ctd_instruments]
    predeploy_form.do_ins_serial_number.choices = [(i.id, i.serial_number) for
                                                   i in do_instruments]

    instruments_list = [(i.id, i.serial_number) for i in Instrument.query.all()]

    deploy_form = DeploymentForm()
    postdeploy_form = PostDeploymentForm()


    if request.method == "GET":
        parameters = Parameter.query.all()
        if deployment.setup_datetime_utc is not None:
            setup_datetime = wdft.util.convert_timezone(
                deployment.setup_datetime_utc, 'UTC', 'America/Chicago')
            predeploy_form.setup_datetime.data = setup_datetime.strftime(
                '%m/%d/%Y %p')
        if deployment.start_datetime_utc is not None:
            start_datetime = wdft.util.convert_timezone(
                deployment.start_datetime_utc, 'UTC', 'America/Chicago')
            predeploy_form.start_datetime.data = start_datetime.strftime(
                '%m/%d/%Y %p')
        # predeploy_form.filename.data = deployment.filename
        predeploy_form.setup_staff_name.data = deployment.setup_staff_name
        predeploy_form.notes.data = deployment.notes
        if len(deployment.instruments):
            for ins in deployment.instruments:
                if set(Parameter.get_ctd_parameters()).issuperset(
                        set(ins.parameters)):
                    predeploy_form.ctd_ins_serial_number.data =\
                        int(ins.id)
                elif set(Parameter.get_do_parameters()).issuperset(
                        set(ins.parameters)):
                    predeploy_form.do_ins_serial_number.data =\
                        int(ins.id)
                else:
                    continue

        if deployment.deployment_datetime_utc is not None:
            deployment_datetime = wdft.util.convert_timezone(
                deployment.deployment_datetime_utc, 'UTC', 'America/Chicago')
            deploy_form.deployment_datetime.data = deployment_datetime.strftime(
                '%m/%d/%Y %p')
        deploy_form.field_tech_names.data = deployment.field_tech_names
        deploy_form.notes.data = deployment.notes

        if deployment.retrieval_datetime_utc is not None:
            retrieval_datetime = wdft.util.convert_timezone(
                deployment.retrieval_datetime_utc, 'UTC', 'America/Chicago')
            postdeploy_form.retrieval_datetime.data = retrieval_datetime.strftime(
                '%m/%d/%Y %p')
        postdeploy_form.notes.data = deployment.notes
        postdeploy_form.filename.data = deployment.filename

        spotchecks = DataValue.query\
                        .filter(DataValue.deployment_id == deployment.id)\
                        .filter(DataValue.is_spotcheck == True)\
                        .order_by(DataValue.datetime_utc)\
                        .all()
        spotcheck_forms = []
        scf = SpotCheckForm()
        scf.instrument_id.choices = instruments_list
        scf.parameter_id.choices = [(p.id, p.abbreviation) for p in parameters]
        spotcheck_forms.append(scf)
        for sc in spotchecks:
            scf = SpotCheckEditForm(obj=sc)
            scf.instrument_id.choices = instruments_list
            scf.parameter_id.choices = [(p.id, p.abbreviation) for p in parameters]
            scf.datetime_utc.data = sc.datetime_utc.astimezone(pytz.timezone('America/Chicago')).strftime(format="%Y-%m-%d %H:%M:%S")
            spotcheck_forms.append(scf)

        calibrations = CalibrationValue.query.filter_by(deployment_id = deployment.id)\
                        .order_by(CalibrationValue.datetime_utc)\
                        .all()
        calibration_forms = []
        cf = CalibrationForm()
        cf.instrument_id.choices = instruments_list
        cf.parameter_id.choices = [(p.id, p.abbreviation) for p in parameters]
        calibration_forms.append(cf)
        for cal in calibrations:
            cf = CalibrationEditForm(obj=cal)
            cf.instrument_id.choices = instruments_list
            cf.parameter_id.choices = [(p.id, p.abbreviation) for p in parameters]
            cf.datetime_utc.data = cal.datetime_utc.astimezone(pytz.timezone('America/Chicago')).strftime(format="%Y-%m-%d %H:%M:%S")
            calibration_forms.append(cf)

        return render_template(
            "admin/deployment.j2", predeploy_form=predeploy_form,
            deploy_form=deploy_form, postdeploy_form=postdeploy_form,
            instruments=instruments_list,
            parameters=parameters,
            calibrations=deployment.calibrations,
            site=deployment.site,
            deployment=deployment,
            spotcheck_forms=spotcheck_forms,
            calibration_forms=calibration_forms,
            form_action=url_for(
                '.deployment_edit', deployment_id=deployment.id,
                deploy_info=deploy_info))
    else:
        if deploy_info == 'predeploy':
            instruments = []
            site_id = int(predeploy_form.site.data)
            # site = Site.query.filter_by(id=site_id).first()
            setup_datetime = parser.parse(
                predeploy_form.setup_datetime.data)
            setup_datetime_utc = wdft.util.cst2utc_with_dst(
                setup_datetime)
            start_datetime = parser.parse(predeploy_form.start_datetime.data)
            start_datetime_utc = wdft.util.cst2utc_with_dst(start_datetime)
            #search_dict = {'id': deployment.id}
            ctd_ins_id = int(predeploy_form.ctd_ins_serial_number.data)
            ctd_instrument = Instrument.query.filter_by(id=ctd_ins_id).first()
            instruments.append(ctd_instrument)

            if predeploy_form.do_ins_serial_number.data:
                do_ins_id = int(predeploy_form.do_ins_serial_number.data)
                do_instrument = Instrument.query.filter_by(id=do_ins_id).first()
                instruments.append(do_instrument)
            
            deployment.site_id = site_id
            deployment.setup_datetime_utc = setup_datetime_utc
            deployment.start_datetime_utc = start_datetime_utc
            deployment.setup_staff_name = predeploy_form.setup_staff_name.data
            deployment.instruments = instruments
            # deployment.filename = predeploy_form.filename.data
            deployment.notes = predeploy_form.notes.data
            db_session.commit()
            flash('predeployment information updated', 'success')
            return redirect(url_for(
                '.deployment_edit', deployment_id=deployment.id))

        elif deploy_info == 'deploy':
            deployment_datetime = parser.parse(
                deploy_form.deployment_datetime.data)
            deployment_datetime_utc = wdft.util.cst2utc_with_dst(
                deployment_datetime)
            search_dict = {'id': deployment.id}
            update_dict = {
                'id': deployment.id,
                'deployment_datetime_utc': deployment_datetime_utc,
                'field_tech_names': deploy_form.field_tech_names.data,
                'notes': deploy_form.notes.data
            }
            wdft.util.sqlalchemy.update_or_new(
                db_session, Deployment, search_dict, update_dict)
            flash('deployment information updated', 'success')
            db_session.commit()
            return redirect(url_for(
                '.deployment_edit', deployment_id=deployment.id))
        elif deploy_info == 'postdeploy':
            retrieval_datetime = parser.parse(
                postdeploy_form.retrieval_datetime.data)
            retrieval_datetime_utc = wdft.util.cst2utc_with_dst(
                retrieval_datetime)
            vertical_offset = postdeploy_form.vertical_offset.data
            deployment.retrieval_datetime_utc = retrieval_datetime_utc
            deployment.vertical_offset = vertical_offset
            deployment.notes = postdeploy_form.notes.data
            f = request.files["file"]
            # print f.read() 
            if request.files['file'].filename:
                f = request.files['file']
                filename = secure_filename(f.filename)
                deployment.filename = filename
                deployment.requires_qaqc = True
                deployment.qaqc_approved = False
                db_session.query(DataValue)\
                    .filter(DataValue.deployment_id == deployment.id)\
                    .filter(DataValue.is_spotcheck == False)\
                    .delete()
                db_session.commit()
                sonde_utils.sonde_upload_helper(
                    deployment, f, vertical_offset=vertical_offset)
            db_session.commit()
            flash('data uploaded', 'success')
            return redirect(url_for(
                '.deployment_edit', deployment_id=deployment.id, _anchor="spot-check-tab"))
        else:
            abort(404)


@admin_blueprint.route('/spot-checks/create', methods=['POST'])
@login_required
def create_spotcheck():

    deployment = Deployment.query.filter_by(id=request.form["deployment_id"]).first()
    print deployment
    if not deployment:
        return abort(404)
    timestamp = parser.parse(request.form["datetime_utc"])
    datetime_utc = wdft.util.cst2utc_with_dst(timestamp)
    datetime_utc = datetime_utc.replace(tzinfo=pytz.UTC)
    dv = DataValue()
    form = SpotCheckForm(request.form)
    form.instrument_id.choices = [(i.id, i.serial_number) for i in Instrument.query.all()]
    form.parameter_id.choices = [(p.id, p.abbreviation) for p in Parameter.query.all()]

    if form.validate_on_submit():
        form.populate_obj(dv)
        dv.datetime_utc = datetime_utc
        dv.site = deployment.site
        dv.is_spotcheck = True
        db_session.add(dv)
        db_session.commit()
        print dv
        return redirect(url_for(
                    '.deployment_edit', deployment_id=deployment.id, _anchor="spot-check-tab"))
    else:
        flash('Something went wrong')
        return redirect(url_for(
                    '.deployment_edit', deployment_id=deployment.id, _anchor="spot-check-tab"))


@admin_blueprint.route('/spot-checks/<int:spot_check_id>', methods=["POST"])
@login_required
def edit_spot_check(spot_check_id):
    form = SpotCheckEditForm(request.form)
    form.instrument_id.choices = [(i.id, i.serial_number) for i in Instrument.query.all()]
    form.parameter_id.choices = [(p.id, p.abbreviation) for p in Parameter.query.all()]
    timestamp = parser.parse(request.form["datetime_utc"])
    datetime_utc = wdft.util.cst2utc_with_dst(timestamp)
    datetime_utc = datetime_utc.replace(tzinfo=pytz.UTC)
    if form.validate_on_submit():
        dv = DataValue.query.filter_by(id=form.id.data).first()
        deployment = Deployment.query.filter_by(id=dv.deployment_id).first()
        form.populate_obj(dv)
        dv.datetime_utc = datetime_utc
        db_session.commit()
        # flash("Edit confirmed")
        return redirect(url_for(
                '.deployment_edit', deployment_id=deployment.id, _anchor="spot-check-tab"))
    else:
        return render_template('admin/alert_failure.html')

@admin_blueprint.route('/spot-checks/<int:spot_check_id>/delete', methods=["POST"])
@login_required
def delete_spot_check(spot_check_id):
    sc = DataValue.query\
            .filter(DataValue.id == spot_check_id)\
            .filter(DataValue.is_spotcheck == True)\
            .first()
    if not sc:
        return abort(404)
    deployment_id = sc.deployment_id
    db_session.query(DataValue)\
            .filter(DataValue.id == spot_check_id)\
            .filter(DataValue.is_spotcheck == True)\
            .delete()
    db_session.commit()
    return "Deleted spotcheck id {id}".format(id=spot_check_id)


@admin_blueprint.route('/calibration-records/create', methods=['POST'])
@login_required
def create_calibration():
    form = CalibrationForm(request.form)
    deployment = Deployment.query.filter_by(id=request.form["deployment_id"]).first()
    if not deployment:
        return abort(404)
    form.parameter_id.choices = [(p.id, p.abbreviation) for p in Parameter.query.all()]
    form.instrument_id.choices = [(i.id, i.serial_number) for i in Instrument.query.all()]
    if form.validate_on_submit():
        datetime = parser.parse(request.form['datetime_utc'])
        datetime_utc = wdft.util.cst2utc_with_dst(datetime).replace(tzinfo=pytz.UTC)
        cv = CalibrationValue()
        form.populate_obj(cv)
        cv.datetime_utc = datetime_utc
        cv.deployment_id = deployment.id
        db_session.add(cv)
        db_session.commit()
        return redirect(url_for(
                '.deployment_edit', deployment_id=deployment.id))
    else:
        flash("Invalid Data", "error")
        return redirect(url_for(
                '.deployment_edit', deployment_id=deployment.id, _anchor="calibration-tab"))


@admin_blueprint.route('/calibration-records/<int:calibration_id>', methods=['POST'])
@login_required
def edit_calibration(calibration_id):
    form = CalibrationEditForm(request.form)
    deployment = Deployment.query.filter_by(id=request.form["deployment_id"]).first()
    if not deployment:
        return abort(404)
    form.parameter_id.choices = [(p.id, p.abbreviation) for p in Parameter.query.all()]
    form.instrument_id.choices = [(i.id, i.serial_number) for i in Instrument.query.all()]
    if form.validate_on_submit():
        cv = CalibrationValue.query.filter_by(id=form.id.data).first()
        datetime = parser.parse(request.form['datetime_utc'])
        datetime_utc = wdft.util.cst2utc_with_dst(datetime).replace(tzinfo=pytz.UTC)
        form.populate_obj(cv)
        cv.datetime_utc = datetime_utc
        db_session.commit()
        return redirect(url_for(
                '.deployment_edit', deployment_id=deployment.id, _anchor="calibration-tab"))
    else:
        return redirect(url_for(
                '.deployment_edit', deployment_id=deployment.id, _anchor="calibration-tab"))


@admin_blueprint.route('/calibration-records/<int:calibration_id>/delete',
                       methods=['POST'])
def calibration_delete(calibration_id):
    calibration = CalibrationValue.query.filter_by(id=calibration_id).first()
    if not calibration:
        abort(404)
    db_session.delete(calibration)
    db_session.commit()

    return "Deleted Calibration id {id}".format(id=calibration_id)


@admin_blueprint.route('/calibration-records/<ins_serial_number>')
@login_required
def calibration_list(ins_serial_number):
    instrument = Instrument.query.filter_by(serial_number=ins_serial_number).first()
    if not instrument:
        abort(404)

    calibrations = CalibrationValue.query.join(Instrument)\
        .filter(Instrument.id == instrument.id).order_by(
            CalibrationValue.datetime_utc.desc()).all()

    return render_template(
        'admin/calibration_list.j2', calibrations=calibrations,
        instrument=instrument)


@admin_blueprint.route("/qaqc/<site_code>", methods=["GET"])
@login_required
def qaqc(site_code):
    site = Site.query.filter_by(site_code=site_code).first()
    if not site:
        abort(404)

    return render_template("admin/qaqc.j2", site=site)


@admin_blueprint.route("/users", methods=["GET"])
@login_required
def user_list():
    users = User.query.all()
    return render_template("admin/user_list.j2", users=users)


@admin_blueprint.route("/users/<user_id>", methods=["GET", "POST"])
@login_required
def user_edit(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        abort(404)
    form = UserEditForm(obj=user)

    roles = Role.query.all()
    form.role_id.choices = [(r.id, r.name) for r in roles]
    agencies = Agency.query.all()
    form.agency_id.choices = [(a.id, a.name) for a in agencies]

    # preset the select dropdowns with the user data. 
    if request.method == "GET":
        form.agency_id.data = user.agency_id
        form.role_id.data = user.role_id

    if form.validate_on_submit():
        form.populate_obj(user)
        user.role_id = form.role_id.data
        user.agency_id = form.agency_id.data
        db_session.commit()
        return redirect(url_for('coastal_admin.user_list'))
    
    return render_template("admin/user_create.j2", form=form,
                            form_action=url_for('coastal_admin.user_edit', user_id=user.id))

@admin_blueprint.route("/users/create", methods=["GET", "POST"])
@login_required
def user_create():
    form = UserCreateForm()
    roles = Role.query.all()
    form.role_id.choices = [(r.id, r.name) for r in roles]
    agencies = Agency.query.all()
    form.agency_id.choices = [(a.id, a.name) for a in agencies]

    if request.method == "GET":
        form.role_id.data = roles[1].id

    else:
        if form.validate():
            user = User()
            user.password = form.password.data
            user.role_id = form.role_id.data
            user.full_name = form.full_name.data
            user.email = form.email.data
            user.agency_id = form.agency_id.data
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('coastal_admin.user_list'))

    return render_template("admin/user_create.j2", form=form, form_action=url_for('coastal_admin.user_create'))


@admin_blueprint.route("/users/<int:user_id>/change-password", methods=["GET", "POST"])
@requires_roles("administrator")
@login_required
def user_change_password(user_id):
    form = UserPasswordChangeForm(request.form)
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return abort(404)
    if request.method == "GET":
        return render_template("admin/user_change_password.j2", form=form, user=user)
    else:
        if form.validate_on_submit():
            return redirect(url_for('coastal_admin.index'))
        else:
            return render_template("admin/user_change_password.j2", form=form, user=user)



@admin_blueprint.route("/instruments", methods=["GET"])
@login_required
def instrument_list():
    instruments = Instrument.query\
        .filter(Instrument.serial_number != "UNDEFINED")\
        .order_by(Instrument.created_date.desc()).all()

    return render_template("admin/instrument_list.j2", instruments=instruments)


@admin_blueprint.route("/instruments/<instrument_id>", methods=["GET", "POST"])
@login_required
def instrument_edit(instrument_id):
    instrument = Instrument.query.filter_by(id=instrument_id).first()
    if not instrument:
        return abort(404)
    form = InstrumentEditForm(obj=instrument)
    if form.validate_on_submit():
        form.populate_obj(instrument)
        instrument.last_modified = datetime.utcnow()
        db_session.commit()
        return redirect(url_for('coastal_admin.instrument_list'))
    
    return render_template("admin/instrument.j2", form=form,
                            form_action=url_for('coastal_admin.instrument_edit', instrument_id=instrument.id))


@admin_blueprint.route("/instruments/create", methods=["GET", "POST"])
@login_required
def instrument_create():
    form = InstrumentForm()

    if form.validate_on_submit():
        inst = Instrument()
        form.populate_obj(inst)
        db_session.add(inst)
        db_session.commit()
        return redirect(url_for('coastal_admin.instrument_list'))

    return render_template("admin/instrument.j2", form=form,
                            form_action=url_for('coastal_admin.instrument_create'))


@admin_blueprint.route("/instruments/<int:instrument_id>/delete", methods=["POST"])
@requires_roles("administrator")
@login_required
def instrument_delete(instrument_id):
    instrument = Instrument.query.filter_by(id=instrument_id).first()
    if not instrument:
        return abort(404)
    db_session.delete(instrument)
    db_session.commit()
    return redirect(url_for('coastal_admin.instrument_list'))


@admin_blueprint.route("/geo/create", methods=["GET", "POST"])
@login_required
def geo_create():
    form = GEOForm()

    if form.validate_on_submit():
        pass

    return render_template("admin/geography.j2", form=form)


@admin_blueprint.route("/agencies", methods=["GET"])
def agency_list():
    ags = Agency.query.all()
    return render_template("admin/agency_list.j2", agencies=ags)


@admin_blueprint.route("/agencies/create", methods=["GET", "POST"])
@login_required
def agency_create():
    form = AgencyForm()

    if form.validate_on_submit():
        ag = Agency()
        form.populate_obj(ag)
        db_session.add(ag)
        db_session.commit()
        return redirect(url_for('coastal_admin.agency_list'))

    return render_template("admin/agency.j2", form=form,
                            page_title="Create Agency",
                            form_action=url_for('coastal_admin.agency_create'))


@admin_blueprint.route("/agencies/<agency_id>", methods=["GET", "POST"])
@login_required
def agency_edit(agency_id):
    agency = Agency.query.filter_by(id=agency_id).first()
    if not agency:
        return abort(404)
    form = AgencyEditForm(obj=agency)
    if form.validate_on_submit():
        form.populate_obj(agency)
        db_session.commit()
        return redirect(url_for('coastal_admin.agency_list'))

    return render_template("admin/agency.j2", form=form,
                           page_title="Edit Agency",
                           form_action=url_for('coastal_admin.agency_edit', agency_id=agency.id))


@admin_blueprint.route("/agencies/<int:agency_id>/delete", methods=["POST"])
@requires_roles("administrator")
@login_required
def agency_delete(agency_id):
    ag = Agency.query.filter_by(id=agency_id).first()
    if not ag:
        return abort(404)
    db_session.delete(ag)
    db_session.commit()
    return redirect(url_for('coastal_admin.agency_list'))

@admin_blueprint.route("/point-measurement-upload", methods=["GET", "POST"])
@requires_roles("administrator")
@login_required
def point_measurements_upload():
    form = PointMeasurementsUploadForm()

    if form.validate_on_submit():
        f = request.files["file"]
        df = load_utils.data_loader.read_point_measurement_data(f)

        try:
            load_utils.data_loader.load_point_measurement_data(df)
        except:
            flash("Something went wrong with that file!")
            return render_template("admin/point_measurements_upload.j2", form=form)
        return redirect(url_for('coastal_admin.index'))

    return render_template("admin/point_measurements_upload.j2", form=form)




