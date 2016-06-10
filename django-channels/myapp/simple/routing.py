from . import consumers

channel_routing = {
    'websocket.connect': consumers.ws_connect,
    'websocket.receive': consumers.ws_receive,
    'websocket.disconnect': consumers.ws_disconnect,

    # Handle http requests here instead of with the normal django views. This
    # isn't very helpful since it removes access to all the awesomeness of
    # django views
    #'http.request': consumers.http_request,

    # a custom channel
    'my.custom.channel': consumers.my_custom_consumer,
}
