from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import HttpResponse
from django.views.generic import View

from .models import Wiggle

class HelloView(LoginRequiredMixin, View):

    login_url = '/world/'

    def get(self, request):
        Wiggle.objects.create()
        print Wiggle.get_wiggle_count()
        return HttpResponse('*')

class WorldView(View):

    def get(self, request):
        Wiggle.objects.create()
        print Wiggle.get_wiggle_count()
        return HttpResponse('*')
