import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

if __name__ == '__main__':
    app = newrelic.agent.application()
    with newrelic.agent.BackgroundTask(app, 'Simple'):
        pass
