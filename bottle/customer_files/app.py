import bottle

import auth.app.app
import auth.app.server.controllers
import ecomm.app.app
import ecomm.app.server.controllers
import lib.bottle.status  # /status
from lib.server.utils import initialize_bottle_sentry_app, make_sentry_client
import rest_api.app.app
import rest_api.app.server.controllers
import stats.app.app
import stats.app.server.controllers
import video_api.app.app
import video_api.app.server.controllers
import version_api.app.app
import version_api.app.server.controllers


def get_application(conf):
    app = bottle.app()
    sentry_client = make_sentry_client(conf)
    app.mount('/auth/',
              initialize_bottle_sentry_app(auth.app.app.app, sentry_client, conf.is_local))
    app.mount('/ecomm/',
              initialize_bottle_sentry_app(ecomm.app.app.app, sentry_client, conf.is_local))
    app.mount('/api/',
              initialize_bottle_sentry_app(rest_api.app.app.app, sentry_client, conf.is_local))
    app.mount('/stats/',
              initialize_bottle_sentry_app(stats.app.app.app, sentry_client, conf.is_local))
    app.mount('/video/',
              initialize_bottle_sentry_app(video_api.app.app.app, sentry_client, conf.is_local))
    app.mount('/version/',
              initialize_bottle_sentry_app(version_api.app.app.app, sentry_client, conf.is_local))

    return app
