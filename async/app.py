import sys
import time
import newrelic.agent

sys.path.append('..')
from utils.decorators import print_nice_transaction_trace


def _ft(name):
    transaction = newrelic.agent.current_transaction()
    return newrelic.agent.FunctionTrace(transaction, name)


def example_1():
    parent = _ft('parent')
    with parent:
        time.sleep(1)

        child = _ft('child')
        with child:
            time.sleep(1)

            child_child = _ft('child_child')
            with child_child:
                time.sleep(1)


def example_2():
    parent = _ft('parent')
    parent.__enter__()
    time.sleep(1)

    child_1 = _ft('child_1')
    child_2 = _ft('child_2')

    child_1.__enter__()
    child_2.__enter__()
    time.sleep(1)
    child_2.__exit__(None, None, None)
    child_1.__exit__(None, None, None)

    parent.__exit__(None, None, None)


def example_3():
    parent = _ft('parent')
    parent.__enter__()
    time.sleep(1)

    child_1 = _ft('child_1')
    child_2 = _ft('child_2')

    child_1.__enter__()
    child_2.__enter__()
    time.sleep(1)
    child_1.__exit__(None, None, None)
    child_2.__exit__(None, None, None)

    parent.__exit__(None, None, None)


def example_4():
    parent = _ft('parent')
    with parent:
        time.sleep(1)
        child_1 = _ft('child_1')

    with child_1:
        time.sleep(1)
        child_2 = _ft('child_2')

    with child_2:
        time.sleep(1)


def example_5():
    parent = _ft('parent')
    child_1 = _ft('child_1')
    child_2 = _ft('child_2')

    parent.__enter__()
    child_1.__enter__()
    child_2.__enter__()

    time.sleep(1)

    parent.__exit__(None, None, None)
    child_1.__exit__(None, None, None)
    child_2.__exit__(None, None, None)


@print_nice_transaction_trace()
@newrelic.agent.background_task()
def main():
    #example_1()
    #example_2()
    example_3()
    #example_4()
    #example_5()


if __name__ == '__main__':
    newrelic.agent.initialize('newrelic.ini')
    newrelic.agent.register_application(timeout=10.0)

    print('--------------------------------------------------')
    main()
    print('--------------------------------------------------')
