from pyramid.view import view_config
import pymongo

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'MyProject'}

@view_config(route_name='hello', renderer='string')
def hello_world(request):
    print '*'
    return '*'

@view_config(route_name='mongo', renderer='string')
def mongo(request):
    client = pymongo.MongoClient('mongo')
    collection = client.my_db.my_collection
    print collection.ensure_index(
            [('flake_worker_ids', pymongo.ASCENDING)],
            unique=True, sparse=True)
    return '*'
