from gevent import monkey; monkey.patch_all(thread=False, socket=False,
        subprocess=False)  # change this to True to produce the "problem"
import multiprocessing as mp


def doit():
    import newrelic.agent

    newrelic.agent.initialize('newrelic.ini')
    app = newrelic.agent.register_application(timeout=10.0)

    @newrelic.agent.background_task()
    def good():
        print('----GOOD----')

    good()


if __name__ == '__main__':
    mp.set_start_method('spawn')
    p = mp.Process(target=doit)
    p.start()
    p.join()
