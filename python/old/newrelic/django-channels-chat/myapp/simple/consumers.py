import json
import time
import newrelic.agent

from channels import Group
from channels.handler import AsgiHandler
from channels.sessions import channel_session
from django.http import HttpResponse


CONNECTIONS = 0

def _encode_text(conn=0, msg=''):
    return json.dumps(
        {
            'connections': str(conn),
            'message': msg,
        }
    )

def _get_group_name(message):
    return message.content['path'].strip('/') or 'None'

@channel_session
def ws_connect(message):
    global CONNECTIONS

    print 'connecting...'
    CONNECTIONS += 1

    path = _get_group_name(message)
    Group(path).add(message.reply_channel)
    Group(path).send({
        'text': _encode_text(CONNECTIONS),
    })

@channel_session
def ws_receive(message):
    global CONNECTIONS
    print 'message received to websocket... "%s"' % message.content['text']

    path = _get_group_name(message)

    text = message.content.get('text')
    if text:
        Group(path).send({
            'text': _encode_text(CONNECTIONS, message.content['text']),
        })

@channel_session
def ws_disconnect(message):
    global CONNECTIONS

    print 'disconnecting...'
    CONNECTIONS -= 1

    path = _get_group_name(message)
    Group(path).discard(message.reply_channel)
    Group(path).send({
        'text': _encode_text(CONNECTIONS),
    })

@newrelic.agent.background_task()
@channel_session
def http_request(message):
    print 'http request...'
    time.sleep(10)

    response = HttpResponse(
        'Hello world! You asked for "%s"' % message.content['path'].strip('/'))
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)

def my_custom_consumer(message):
    print 'I got a message!'
