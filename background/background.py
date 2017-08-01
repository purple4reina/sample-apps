import newrelic.agent

newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)


def func():
    pass


@newrelic.agent.background_task()
def main():
    transaction = newrelic.agent.current_transaction()

    if not transaction:
        return

    with newrelic.agent.FunctionTrace(transaction, '__main__:func'):
        return func()


if __name__ == '__main__':
    main()
