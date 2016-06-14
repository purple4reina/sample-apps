import time

from django.http import HttpResponse
from django.shortcuts import render

from .models import Dumbo
import toxiproxy_controller

def timeing(fn):
    def wrap(*args, **kwargs):
        start = time.time()
        ret = fn(*args, **kwargs)
        print 'It took %s seconds!' % (time.time() - start)
        if False:
            print 'current toxic is: %s' % toxiproxy_controller.get_toxic()
        return ret
    return wrap

@timeing
def create_many(request, number):
    try:
        number = int(number)
    except ValueError:
        err = '"%s" is not a number, please try again' % number
        return render(request, 'dumbapp/create_many.html', {
            'err': err,
        })

    initial_num = Dumbo.objects.count()

    Dumbo.objects.bulk_create([
        Dumbo(name='Dumbo %s' % time.time()) for _ in xrange(number)
    ], batch_size=99)

    current_num = Dumbo.objects.count()

    return render(request, 'dumbapp/create_many.html', {
        'initial_num': initial_num,
        'current_num': current_num,
        'number': number,
    })


@timeing
def delete_all(request):
    initial_num = Dumbo.objects.count()
    Dumbo.objects.all().delete()
    current_num = Dumbo.objects.count()

    return render(request, 'dumbapp/delete_all.html', {
        'initial_num': initial_num,
        'current_num': current_num,
    })


@timeing
def hit(request):
    """
    A simple hit to the db, returning empty page, helpful for simple testing
    """
    Dumbo.objects.count()
    return HttpResponse('OK')
