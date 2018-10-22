import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

import functools
import multiprocessing


# EXAMPLE ONE

def subprocessed_background_task(*bt_args, **bt_kwargs):
    def _register_wrapper(func):
        @functools.wraps(func)
        def _wrap_func(*args, **kwargs):
            newrelic.agent.register_application(timeout=10.0)
            try:
                return newrelic.agent.background_task(*bt_args,
                        **bt_kwargs)(func)(*args, **kwargs)
            finally:
                newrelic.agent.shutdown_agent()
        return _wrap_func
    return _register_wrapper


@subprocessed_background_task()
def say_hello(name):
    print('Hello %s!' % name)


if __name__ == '__main__':
    p = multiprocessing.Process(target=say_hello, args=('New Relic',))
    p.start()
    p.join()


# EXAMPLE TWO

class NRProcess(multiprocessing.Process):

    def __init__(self, name, *args, **kwargs):
        self.hello_name = name
        super(NRProcess, self).__init__(*args, **kwargs)

    def run(self):
        app = newrelic.agent.register_application(timeout=10.0)

        with newrelic.agent.BackgroundTask(application=app, name='say_hello'):
            print('Hello %s!' % self.hello_name)

        newrelic.agent.shutdown_agent()


if __name__ == '__main__':
    p = NRProcess('New Relic')
    p.start()
    p.join()
