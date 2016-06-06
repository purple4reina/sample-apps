from channels import Group
from channels.sessions import channel_session


@channel_session
def ws_connect(message):
    print 'connecting...'
    path = message.content['path']
    Group(path).add(message.reply_channel)
    group = Group(path)
    print 'dir(group): ', dir(group)
    print 'len(group): ', len(group)
    print 'there are now %d connections' % 1

@channel_session
def ws_receive(message):
    print 'message received...'

@channel_session
def ws_disconnect(message):
    print 'disconnecting...'
    path = message.content['path']
    Group(path).discard(message.reply_channel)
    print 'there are now %d connections' % 1
