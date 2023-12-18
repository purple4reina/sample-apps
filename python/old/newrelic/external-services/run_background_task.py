import newrelic.agent
from threading import Thread

from mytest_package import myfunction

application = newrelic.agent.register_application(timeout=10.0)


def do_something_with_backgroundtask(num):
    with newrelic.agent.BackgroundTask(application, name=__name__,
            group='Present'):
        for _ in xrange(num):
            myfunction()

def do_something(num):
    for _ in xrange(num):
        myfunction()

if __name__ == '__main__':

    # Run a task that has the `with` statement inside a new thread.
    # When the `with newrelic.agent.BackgroundTask` is in the
    # `do_something_with_backgroundtask` function, the external transaction
    # gets recorded in APM.
    thread = Thread(target=do_something_with_backgroundtask, args=(100,))
    thread.start()
    thread.join()
    print 'Finished performing first calculations'

    # Run a similar task where the `with` statement is not in the thread.
    # When the `with newrelic.agent.BackgroundTask` is in the `if __name__ ==
    # __main__` section, the external transaction does NOT get recorded in APM.
    with newrelic.agent.BackgroundTask(application, name=__name__,
            group='NotPresent'):
        thread = Thread(target=do_something, args=(100,))
        thread.start()
        thread.join()
    print 'Finished performing second calculations'

    # Lastly, run the task outside of a thread. The external service
    # transaction gets recorded in APM.
    with newrelic.agent.BackgroundTask(application, name=__name__,
            group='NoThread'):
        do_something(100)
    print 'Finished performing third calculations'
