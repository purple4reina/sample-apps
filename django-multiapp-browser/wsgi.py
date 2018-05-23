import os

from django.core.wsgi import get_wsgi_application

class WsgiWrapper:
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO')
        # if path_info == '/power/':
        #     environ['newrelic.app_name'] = 'TM3;TM'
        # elif path_info in ('/touch/', '/x/ra/'):
        #     environ['newrelic.app_name'] = 'Touch;TM3;TM'
        environ['newrelic.app_name'] = path_info.strip('/')
        environ['PATH_INFO'] = '/'

        return self.application(environ, start_response)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_wsgi_application()
application = WsgiWrapper(application)
