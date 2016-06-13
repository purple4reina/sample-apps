import time

from django.shortcuts import render

from .models import Dumbo


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


def delete_all(request):
    initial_num = Dumbo.objects.count()
    Dumbo.objects.all().delete()
    current_num = Dumbo.objects.count()

    return render(request, 'dumbapp/delete_all.html', {
        'initial_num': initial_num,
        'current_num': current_num,
    })
