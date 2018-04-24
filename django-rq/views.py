from django.http import HttpResponse
from django.views import View

import django_rq


def do_work():
    import newrelic.agent
    app = newrelic.agent.register_application(timeout=10.0)
    newrelic.agent.record_custom_metric('Custom/value', 1, app)
    print('I did some work!')
    newrelic.agent.shutdown_agent()


class Index(View):
    def get(self,  request):
        django_rq.enqueue(do_work)
        return HttpResponse('*')
