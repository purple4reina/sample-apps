import newrelic.agent

newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10.0)

import sys

sys.path.append('tests')

import pysolr
from testing_support.settings import solr_settings


HOST, PORT = solr_settings()


@newrelic.agent.background_task()
def main():
    solr = pysolr.Solr('http://%s:%s/solr' % (HOST, PORT), timeout=10)
    results = solr.search('bananas')
    print 'results: ', results
    print 'len(results): ', len(results)


if __name__ == '__main__':
    print '----------------------------------------'
    main()
    print '----------------------------------------'
