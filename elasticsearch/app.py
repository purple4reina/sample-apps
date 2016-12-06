import newrelic.agent
import os
from random import randint

newrelic.agent.initialize(os.environ.get('NEW_RELIC_CONFIG_FILE'))
app = newrelic.agent.register_application(timeout=10.0)

import elasticsearch

ES_URLS = ['http://elasticsearch_%s:9200' % i for i in xrange(1, 3)]

def _log(*args):
    print '\033[1;91m' + '=' * randint(2, 8) + '>\033[0m ' + ' '.join(map(str, args))

def wait_for_ready():
    for url in ES_URLS:
        client = elasticsearch.Elasticsearch(url)
        while not client.ping():
            pass

def info():
    client = elasticsearch.Elasticsearch(ES_URLS)
    info = client.info()
    _log('info: ', info)

def _exercise_es():
    es = elasticsearch.Elasticsearch(ES_URLS)

    es.index("contacts", "person",
            {"name": "Joe Tester", "age": 25, "title": "QA Master"}, id=1)
    es.index("contacts", "person",
            {"name": "Jessica Coder", "age": 32, "title": "Programmer"}, id=2)
    es.index("contacts", "person",
            {"name": "Freddy Tester", "age": 29, "title": "Assistant"}, id=3)
    es.indices.refresh('contacts')
    es.index("address", "employee", {"name": "Sherlock",
        "address": "221B Baker Street, London"}, id=1)
    es.index("address", "employee", {"name": "Bilbo",
        "address": "Bag End, Bagshot row, Hobbiton, Shire"}, id=2)
    es.search(index='contacts', q='name:Joe')
    es.search(index='contacts', q='name:jessica')
    es.search(index='address', q='name:Sherlock')
    es.search(index=['contacts', 'address'], q='name:Bilbo')
    es.search(index='contacts,address', q='name:Bilbo')
    es.search(index='*', q='name:Bilbo')
    es.search(q='name:Bilbo')
    #es.indices.status()
    es.cat.health()
    es.cluster.health()
    es.nodes.info()
    es.snapshot.status()

def main():
    _log('Playing with client.info()')
    info()

    _log('Like we\'re in the tests')
    _exercise_es()

if __name__ == '__main__':
    wait_for_ready()
    with newrelic.agent.BackgroundTask(app, 'ElasticSearch'):
        main()
