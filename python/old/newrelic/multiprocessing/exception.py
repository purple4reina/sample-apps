import json

from multiprocessing import Process


def main():
    import newrelic.agent
    newrelic.agent.initialize('newrelic.ini')
    application = newrelic.agent.register_application(timeout=10.0)

    try:
        responseData = json.loads('asdfasdfasdf')
    except Exception as e:
        newrelic.agent.record_exception(application=application)

    newrelic.agent.shutdown_agent()


if __name__ == '__main__':
    for _ in range(10):
        p = Process(target=main)
        p.start()
        p.join()
