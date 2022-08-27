import time
import newrelic.agent

from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

from .models import Dumbo
import toxiproxy_controller

def timeing(fn):
    def wrap(*args, **kwargs):
        start = time.time()
        ret = fn(*args, **kwargs)
        print 'It took %s seconds!' % (time.time() - start)
        if settings.USE_TOXIPROXY:
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
    ])

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


@timeing
def go_away(request):
    with toxiproxy_controller.NoMySqlServer():
        try:
            Dumbo.objects.create(name='Dumbo %s' % time.time())
        except:
            print 'shutting down...'
            newrelic.agent.shutdown_agent(timeout=5)
            print 're-raising error...'
            raise
    return HttpResponse('OK')


@timeing
def latency_connection(request, latency=None):
    with toxiproxy_controller.MySqlLatency(latency):
        print 'hitting the db now...'
        Dumbo.objects.create(name='Dumbo %s' % time.time())
    return HttpResponse('OK')
