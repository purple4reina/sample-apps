import newrelic.agent

from helloworld.lib.base import BaseController, render

class CatsController(BaseController):

    def index(self):
        newrelic.agent.add_custom_parameter('hello', 'cats')
        newrelic.agent.capture_request_params(flag=True)
        # Return a rendered template
        #return render('/cats.mako')
        # or, return a string
        return 'Hello Cats!\n'
