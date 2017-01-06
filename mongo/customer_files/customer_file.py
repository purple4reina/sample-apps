# rey added the imports here
from pymongo import MongoClient
from pymongo.errors import AutoReconnect
from types import MethodType
from functools import wraps
import inspect

# There's auto reconnect logic handling on the collection object. When we get
# the collection we wrap it like so:

def reconnect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 1800 # seconds
        num_fails = 0
        while 1:
            try:
                return func(*args, **kwargs)
            except AutoReconnect, e:
                num_fails += 1
                time.sleep(1)
                if num_fails >= max_retries:
                    raise e
    return wrapper

def get_mongo_collection(business_id, unqualified_name):
    """
    Returns the MongoCollection instance for the specified business and
    collection name.

    Key idea here is that *for any given HTTP request*, operations are
    generally confined to collections within a particular business.

    :type business_id: basestring
    :type unqualified_name: basestring
    :rtype: pymongo.collection.Collection
    """
    coll = get_mongo_database()["{}_{}".format(business_id, unqualified_name)]

    # wrap the mongo collection object with mongo reconnect wrapper
    class MongoWrapper:
        def __init__(self, other):
            self.other = other

        def __getattr__(self, name):
            if hasattr(self.other, name):
                func = getattr(self.other, name)
                return lambda *args, **kwargs: self._wrap(func, args, kwargs)
            raise AttributeError(name)

        def _wrap(self, func, args, kwargs):
            if type(func) == MethodType:
                result = reconnect(func)(*args, **kwargs)
            else:
                result = reconnect(func)(self.other, *args, **kwargs)
            return result

    return MongoWrapper(coll)

# rey wrote this part too
class get_mongo_database(dict):
    def __getitem__(self, name):
        client = MongoClient('mongo')
        return client.my_db.my_collection
