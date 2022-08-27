#!/usr/bin/env python
import sys
sys.path.append('./')
from lib.scripts.main import main_noargs

import bottle
import gevent
from raven import Client

import app
import db.config
from lib import consts
from lib.bottle.recycler import activate
import lib.gflags as gflags
from lib.logging import timeseries
import lib.scripts.env
from lib.server.utils import initialize_bottle_root_app
from lib.utils.status import status_worker

FLAGS = gflags.FLAGS

gflags.DEFINE_integer(
    'bottle-port',
    8001,
    'port number')

if __name__ == "__main__":
    def run():
        conf = db.config.create_app(lib.scripts.env.FLAGS.env)
        application = initialize_bottle_root_app(app.get_application(conf), conf, consts.PELOTON)
        timeseries.configure_logger()
        gevent.spawn(status_worker, Client(conf.sentry_url).captureException)
        activate()
        bottle.run(app=application,
                   host="0.0.0.0",
                   port=FLAGS.bottle_port,
                   quiet=True,
                   server="gevent",
                   reloader=conf.is_local)

    sys.exit(main_noargs(sys.argv, run))
