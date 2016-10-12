import random
import requests
import cPickle as pickle

import newrelic.agent

from django.shortcuts import HttpResponse
from django.views.generic import View

class Pickler(object):
    @classmethod
    def pickle(cls, obj):
        pickled_obj = pickle.dumps(obj)
        unpickled_obj = pickle.loads(pickled_obj)
        return unpickled_obj

class Clarinet(object):

    def __init__(self):
        self.keys = random.randrange(10000)
        print self.keys

class APIView(View):

    def get(self, request):
        this_obj = Clarinet()
        keys = this_obj.keys
        new_obj = Pickler.pickle(this_obj)
        assert new_obj.keys == keys
        return HttpResponse('{}')

class ClientView(View):

    def get_api_data(self):
        response = requests.get('http://localhost:8000/api/')
        assert response.ok
        return response.json()

    def get(self, request):
        data = self.get_api_data()
        return HttpResponse(str(data))
