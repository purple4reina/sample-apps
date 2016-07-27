import datetime
import locale

from flask import Flask, Blueprint, render_template, send_from_directory
from flask.ext import assets
from flask.ext.babel import Babel
import newrelic.agent
import numpy as np

# for number formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
    except:
        locale.setlocale(locale.LC_ALL, 'english-us')


def create_app(blueprints=None):
    """app factory for drought app"""
    if blueprints and isinstance(blueprints, Blueprint):
        blueprints = [blueprints]

    # initialize app
    app = Flask('wdft')

    # note: you must set jinja options before the jinja environment is created,
    # so now is a good time
    jinja_extensions = [
        'jinja2.ext.autoescape',
        'jinja2.ext.do',
        'jinja2.ext.with_',
    ]
    app.jinja_options = {
        'extensions': jinja_extensions,
    }

    # initialize Babel and set default date formatting
    babel = Babel(app)
    babel.date_formats['date'] = 'short'
    babel.date_formats['date.short'] = 'yyyy-MM-dd'
    babel.date_formats['datetime'] = 'short'
    babel.date_formats['datetime.short'] = 'yyyy-MM-dd HH:mm:ss'

    # initialize Flask-Assets
    assets_env = assets.Environment(app)
    # assets_env.register(
    #     'wdft_ie_lte8',
    #     assets.Bundle(
    #         'js/r2d3/r2d3.js',
    #         'js/json2/json2.js',
    #         'js/es5-shim/es5-shim.js',
    #         'js/polyfill/typedarray.js',
    #         filters='rjsmin',
    #         output='gen/ie_lte8.min.js',
    #     )
    # )
    # assets_env.register(
    #     'wdft_modern_browsers',
    #     assets.Bundle(
    #         'js/d3/d3.js',
    #         filters='rjsmin',
    #         output='gen/modern_browsers.min.js',
    #     )
    # )
    # assets_env.register(
    #     'wdft_base',
    #     assets.Bundle(
    #         # note: need to load bootstrap and angular after jquery
    #         #'js/jquery/jquery-1.8.2.js',
    #         # 'components/jquery/dist/jquery.min.js',
    #         # 'js/jquery-ui/jquery-ui-1.10.3.custom.js',
    #         # 'components/bootstrap-3.3.5-dist/js/bootstrap.min.js',
    #         #'js/angular/angular.js',
    #         #'js/angular-resource/angular-resource.js',
    #         # 'js/bootstrap/bootstrap.js',
    #         'js/retinajs/retina.js',
    #         #'js/moment.js',
    #         #'js/select2/select2.js',
    #         #'js/topojson/topojson.js',
    #         'js/underscore/underscore.js',
    #         'js/underscore.string/underscore.string.js',
            
    #         # 'js/wdft.js',
    #         filters='rjsmin',
    #         output='gen/wdft_base.min.js',
    #     )
    # )
    # assets_env.register(
    #     'wdft_js',
    #     assets.Bundle(
    #         # note: need to load bootstrap and angular after jquery
    #         #'js/jquery/jquery-1.8.2.js',
    #         #'js/jquery-ui/jquery-ui-1.10.3.custom.js',
    #         #'js/angular/angular.js',
    #         #'js/angular-resource/angular-resource.js',
    #         #'js/bootstrap/bootstrap.js',
    #         #'js/retinajs/retina.js',
    #         'js/moment.js',
    #         # 'js/select2/select2.js',
    #         'js/topojson/topojson.js',
    #         #'js/underscore/underscore.js',
    #         #'js/underscore.string/underscore.string.js',
    #         #'js/wdft.js',
    #         filters='rjsmin',
    #         output='gen/wdft.min.js',
    #     )
    # )

    # assets_env.register(
    #     'wdft_css',
    #     assets.Bundle(
    #         # 'css/bootstrap/bootstrap.css',
    #         # 'css/bootstrap/bootstrap-responsive.css',
    #         'js/select2/select2.css',
    #         assets.Bundle(
    #             'css/font-awesome/css/font-awesome.css',
    #             filters=[
    #                 webassets.filter.get_filter(
    #                     'cssrewrite', replace=lambda url: re.sub(
    #                         r'^../font/', '../css/font-awesome/font/', url)),
    #             ],
    #         ),
    #         assets.Bundle(
    #             'css/jquery-ui/smoothness/jquery-ui-1.10.3.custom.css',
    #             filters=[
    #                 webassets.filter.get_filter(
    #                     'cssrewrite', replace=lambda url: re.sub(
    #                         r'^images/', '../css/jquery-ui/smoothness/images/',
    #                         url)),
    #             ],
    #         ),
    #         assets.Bundle(
    #             assets.Bundle(
    #                 'css/wdft/wdft.css', filters=None, output='gen/wdft.css'),
    #             # filters=[
    #             #     webassets.filter.get_filter('cssrewrite', replace=lambda url: re.sub(r'^../fonts/', '../css/fonts/', url)),
    #             #     webassets.filter.get_filter('cssrewrite', replace=lambda url: re.sub(r'^../img/', '../css/img/', url)),
    #             # ],
    #         ),
    #         filters=[
    #             'cssmin',
    #         ],
    #         output='gen/wdft.min.css',
    #     )
    # )

    assets_env.register(
        'wdft_css',
        assets.Bundle(
            'css/wdft/wdft.css',
            filters=None,
            output='gen/wdft.css'
        ),
    )

    assets_env.init_app(app)

    # configure common things from config.py
    app.config.from_object('wdft.config')

    # register blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        if value:
            return value.strftime(format)

    def format_number(number, decimal_places=0):
        if number is None or np.isnan(float(number)):
            return '- n.a. -'
        else:
            format_str = "%%.%(decimal_places)sf" % {"decimal_places": decimal_places}
        return locale.format(format_str, number, grouping=True)

    def format_string(string):
        if string is None or str(string) == 'nan':
            return '-n/a-'
        else:
            return str(string)

    def newrelic_browser_timing_header():
        if app.config.get('NEW_RELIC_ENABLED', False):
            return newrelic.agent.get_browser_timing_header()
        else:
            return ''

    def newrelic_browser_timing_footer():
        if app.config.get('NEW_RELIC_ENABLED', False):
            return newrelic.agent.get_browser_timing_footer()
        else:
            return ''

    def today():
        return datetime.datetime.today().strftime('%Y-%m-%d')

    @app.route('/policies/')
    def policies():
        return render_template('wdft/policies.html')

    @app.route('/')
    def index():
        return render_template('wdft/landing.html')

    @app.route('/about')
    def about():
        packages = (
            #('name', 'link', 'description'),
            ('celery', 'http://celeryproject.org', """
                Celery is an asynchronous task queue/job queue based on distributed
                message passing. It is focused on real-time operation, but supports
                scheduling as well."""),
            ('flask', 'http://flask.pocoo.org', """
                A lightweight Python web framework based on Werkzeug and Jinja
                2."""),
            ('ipython', 'http://ipython.org', """
                IPython provides tools for interactive and parallel computing that
                are widely used in scientific computing."""),
            ('matplotlib', 'http://matplotlib.org', """
                matplotlib is a python 2D plotting library which produces
                publication quality figures in a variety of hardcopy formats and
                interactive environments across platforms."""),
            ('nginx', 'http://nginx.org', """
                Nginx is a free, open-source, high-performance HTTP server and
                reverse proxy, as well as an IMAP/POP3 proxy server."""),
            ('numpy', 'http://numpy.scipy.org', """
                NumPy is the fundamental package for scientific computing with
                Python."""),
            ('pandas', 'http://pandas.pydata.org', """
                pandas is an open source library providing high-performance,
                easy-to-use data structures and data analysis tools for the Python
                programming language."""),
            ('postgres', 'http://www.postgresql.org', """
                PostgreSQL is a powerful, open source object-relational database
                system. It has more than 15 years of active development and a proven
                architecture that has earned it a strong reputation for reliability,
                data integrity, and correctness."""),
            ('postgis', 'http://postgis.refractions.net', """
                PostGIS adds support for geographic objects to the PostgreSQL
                object-relational database. In effect, PostGIS "spatially enables"
                the PostgreSQL server, allowing it to be used as a backend spatial
                database for geographic information systems (GIS)"""),
            ('scipy', 'http://www.scipy.org', """
                SciPy is open-source software for mathematics, science, and
                engineering."""),
            ('sqlalchemy', 'http://www.sqlalchemy.org', """
                SQLAlchemy is the Python SQL toolkit and Object Relational Mapper
                that gives application developers the full power and flexibility of
                SQL."""),
            ('redis', 'http://redis.io', """
                Redis is an open source, advanced key-value store. It is often
                referred to as a data structure server since keys can contain
                strings, hashes, lists, sets and sorted sets."""),
        )
        return render_template('wdft/about.html', packages=packages)


    @app.route('/disclaimer')
    def disclaimer():
        return render_template('wdft/disclaimer.html')

    @app.route('/robots.txt')
    def robots():
        return send_from_directory(app.static_folder, "robots.txt")

    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['format_number'] = format_number
    app.jinja_env.filters['format_string'] = format_string
    app.jinja_env.globals['newrelic_browser_timing_header'] = newrelic_browser_timing_header
    app.jinja_env.globals['newrelic_browser_timing_footer'] = newrelic_browser_timing_footer
    app.jinja_env.globals['today'] = today
    # app.jinja_env.globals['global_nav'] = app.config['GLOBAL_NAV']

    return app
