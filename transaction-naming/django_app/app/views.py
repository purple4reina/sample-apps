import newrelic

from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView

from .models import ConjoinedTriangle

class BaseView(View):
    def get(self, request):
        return HttpResponse('*')

class EarthView(BaseView):
    pass

class MarsView(BaseView):
    pass

class ConjoinedTriangleListView(ListView):
    model = ConjoinedTriangle
