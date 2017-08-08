from django.shortcuts import render
from django.http import HttpResponse

import channels


def home(request):
    return render(request, 'simple/home.html', {})

def custom_channel(request):
    channel = channels.Channel('my.custom.channel')
    channel.send({'number': 1})
    return HttpResponse('hello my custom channel!')
