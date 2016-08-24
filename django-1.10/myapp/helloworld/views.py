from django.shortcuts import HttpResponse

# Create your views here.

def hello(request):
    return HttpResponse('hello')

def index(request):
    return HttpResponse('')

def err(request):
    raise CustomException

class CustomException(Exception):
    pass
