import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
application = newrelic.agent.register_application(timeout=10.0)


with newrelic.agent.BackgroundTask(application, 'something', 'Uri') as txn:
    txn.background_task = False
