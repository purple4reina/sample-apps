import newrelic.agent

newrelic.agent.initialize('newrelic-1.ini')
app1 = newrelic.agent.register_application(timeout=10.0)

newrelic.agent.initialize('newrelic-2.ini')
app2 = newrelic.agent.register_application(timeout=10.0)

def main():
    pass

if __name__ == '__main__':
    with newrelic.agent.BackgroundTask(app1, 'BackgroundTask'):
        main()
    with newrelic.agent.BackgroundTask(app2, 'BackgroundTask'):
        main()
