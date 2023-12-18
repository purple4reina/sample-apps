try:
    # When bootstrapping with newrelic, import the agent before anything else
    import newrelic.agent
except ImportError:
    newrelic = None

from django.core.wsgi import get_wsgi_application

class WsgiWrapper:
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        # This overrides the application name for /power/ and '/touch/' so we
        # can get some additional single-page AJAX metrics
        path_info = environ.get('PATH_INFO')
        if path_info == '/power/':
            environ['newrelic.app_name'] = 'TM3;TM'
        elif path_info in ('/touch/', '/x/ra/'):
            environ['newrelic.app_name'] = 'Touch;TM3;TM'

        return self.application(environ, start_response)

application = get_wsgi_application()
if newrelic:
    application = WsgiWrapper(application)
