import requests
import cPickle as pickle

from django.shortcuts import HttpResponse
from django.views.generic import View

from .models import Wiggle

QUERY_SET = None

class APIView(View):

    def pickle_it(self, new_obj):
        global QUERY_SET

        if QUERY_SET:
            old_obj = pickle.loads(QUERY_SET)

        old_str = QUERY_SET
        QUERY_SET = pickle.dumps(new_obj)
        assert old_str != QUERY_SET

        return old_obj

    def get(self, request):
        Wiggle.objects.create()
        new_obj = Wiggle.objects.last()
        old_obj = self.pickle_it(new_obj)
        print old_obj.id
        assert old_obj.id != new_obj.id
        return HttpResponse('{}')

class ClientView(View):

    def get_api_data(self):
        response = requests.get('http://localhost:8000/api/')
        assert response.ok
        return response.json()

    def get(self, request):
        data = self.get_api_data()
        return HttpResponse(str(data))
