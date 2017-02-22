from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from .models import Foo


### Caught by New Relic agent ###

def FunctionViewExample(request):
    return render(request, "testcase.html")


### Whereas class based views not caught by New Relic agent ###

class ListViewExample(ListView):
    # https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-display/
    # https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#listview
    model = Foo
    template_name = "testcase.html"


class TemplateViewExample(TemplateView):
    # https://docs.djangoproject.com/en/1.10/ref/class-based-views/base/#templateview
    template_name = "testcase.html"
