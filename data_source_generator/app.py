import time
import newrelic.agent


@newrelic.agent.data_source_generator(name='Custom Metrics')
def custom_metrics():
    yield ('Custom/Rey/Time', time.time())


if __name__ == '__main__':
    newrelic.agent.initialize()
    newrelic.agent.register_application()
    newrelic.agent.register_data_source(custom_metrics)

    # run forever
    while True:
        pass
