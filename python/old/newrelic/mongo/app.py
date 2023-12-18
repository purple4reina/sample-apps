import os
WITH_AGENT = os.environ.get('USE_AGENT', True) in [True, 'True', 'true', '1']

if WITH_AGENT:
    import newrelic.agent

    newrelic.agent.initialize(os.environ.get('NEW_RELIC_CONFIG_FILE'))
    app = newrelic.agent.register_application(timeout=10.0)

import pymongo
from customer_files.customer_file import get_mongo_collection

def main():
    client = pymongo.MongoClient('mongo')
    collection = get_mongo_collection('hello', 'world')
    print collection.ensure_index(
            [('flake_worker_ids', pymongo.ASCENDING)],
            unique=True, sparse=True)

if __name__ == '__main__':
    if WITH_AGENT:
        with newrelic.agent.BackgroundTask(app, 'Mongo'):
            main()
    else:
        main()
