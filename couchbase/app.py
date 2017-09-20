import os
import newrelic.packages.requests as requests
import sys
import time

import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application(timeout=10)

from couchbase.exceptions import HTTPError
from couchbase.bucket import Bucket
from couchbase.n1ql import N1QLQuery

sys.path.append('..')
from utils.decorators import print_nice_transaction_trace


DOCKER_HOST = os.environ.get('DOCKER_HOST').split('//')[1].split(':')[0]


def random_word(length=None):
    url = 'http://setgetgo.com/randomword/get.php'
    if length:
        url += '?len=%s' % length
    resp = requests.get(url)
    return resp.text.lower()


@print_nice_transaction_trace()
@newrelic.agent.background_task()
def main():
    bucket = Bucket('couchbase://%s/default' % DOCKER_HOST)
    username = random_word(length=10).title()
    now = time.time()

    result = bucket.upsert(username, {
        'name': username,
        'created': now,
        'interests': [random_word(length=i) for i in range(3, 10)],
    })
    assert result.success

    try:
        # only need to do this once, else it fails
        bucket.n1ql_query('CREATE PRIMARY INDEX ON default').execute()
    except HTTPError:
        pass

    row_iter = bucket.n1ql_query(
            N1QLQuery('SELECT name FROM default WHERE created > $1',
                now - 10 * 60))

    for row in row_iter:
        print row


if __name__ == '__main__':
    print '----------------------------------------'
    main()
    print '----------------------------------------'
