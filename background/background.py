import newrelic.agent

newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)



@newrelic.agent.background_task()
def main():
    pass


if __name__ == '__main__':
    main()
