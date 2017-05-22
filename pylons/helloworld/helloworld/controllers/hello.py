import newrelic.agent

from helloworld.lib.base import BaseController, render

class HelloController(BaseController):

    def index(self):
        newrelic.agent.add_custom_parameter('hello', 'world')
        newrelic.agent.capture_request_params(flag=True)
        # Return a rendered template
        return render('/hello.mako')
        # or, return a string
        #return '*'
