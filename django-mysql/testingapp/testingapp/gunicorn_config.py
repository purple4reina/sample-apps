import newrelic.agent


def _worker_abort(worker):
    print 'executing worker_abort hook...'
    #newrelic.agent.shutdown_agent(timeout=5.0)
    #print 'agent shutdown complete!!'


worker_abort = _worker_abort
django_settings = 'testingapp.settings'
timeout = 2
loglevel = 'DEBUG'
errorlog = '-'
