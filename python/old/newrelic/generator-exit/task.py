import newrelic.agent
import newrelic.api

newrelic.agent.initialize('newrelic.ini')
app = newrelic.agent.register_application(timeout=10.0)
transaction = newrelic.api.transaction.Transaction(app, enabled=True)


def foo():
    with transaction:
        for i in xrange(3):
            yield i


f = foo()
f.next()
f.close()
