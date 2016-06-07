from channels import Group
from channels.sessions import channel_session


@channel_session
def ws_connect(message):
    print 'connecting...'

@channel_session
def ws_receive(message):
    print 'message received...'

@channel_session
def ws_disconnect(message):
    print 'disconnecting...'
