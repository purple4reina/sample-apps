import celerytasks

from django.http import HttpResponse


# Create your views here.
def home(request):
    return HttpResponse('hello world')


def celery(request):
    print 'slowly...'
    celerytasks.slowly.delay(5)
    return HttpResponse('hello celery')
