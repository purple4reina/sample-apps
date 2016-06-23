import newrelic.agent

from mytest_package import myfunction

application = newrelic.agent.register_application(timeout=10.0)

def main():
    with newrelic.agent.BackgroundTask(application, name=__name__,
            group='Task'):
        for _ in xrange(100):
            myfunction()


if __name__ == '__main__':
    main()
