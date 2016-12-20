import os
import newrelic.agent

newrelic.agent.initialize(os.environ.get('NEW_RELIC_CONFIG_FILE'))
app = newrelic.agent.register_application(timeout=10.0)

import pymongo

def main():
    client = pymongo.MongoClient('mongo')
    collection = client.my_db.my_collection
    print collection.ensure_index(
            [('flake_worker_ids', pymongo.ASCENDING)],
            unique=True, sparse=True)

if __name__ == '__main__':
    with newrelic.agent.BackgroundTask(app, 'Mongo'):
        print '----------------------------------------'
        main()
        print '----------------------------------------'
