import time
import newrelic.agent


@newrelic.agent.data_source_generator(name='Custom Metrics')
def custom_metrics():
    yield ('Custom/Rey/Time', time.time())


def custom_source(settings):
    def custom_metrics():
        yield ('Custom/Reina/Time', time.time())

    def custom_metrics_factory(environ):
        return custom_metrics

    properties = {}
    properties['factory'] = custom_metrics_factory
    properties['name'] = 'Reina Time'

    return properties


if __name__ == '__main__':
    newrelic.agent.initialize()
    newrelic.agent.register_application()
    newrelic.agent.register_data_source(custom_metrics)
    newrelic.agent.register_data_source(custom_source)

    # run forever
    while True:
        time.sleep(1)
