from django.http import HttpResponse
from django.views import View

class BaseView(View):
    def get(self, request):
        return HttpResponse('*')
