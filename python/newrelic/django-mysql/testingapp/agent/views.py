import newrelic.agent

from django.http import HttpResponse


def shutdown_agent(request):
    newrelic.agent.shutdown_agent(timeout=5)
    return HttpResponse('agent shutdown complete')
