import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import bottle


@newrelic.agent.background_task()
def main():
    bottle.hello_world()


if __name__ == '__main__':
    main()
