# Tornado Zmq

This is an example app that uses Tornado, ZeroMQ, and Tornado's
curl_httpclient.

As of the writing of this README, the New Relic Python Agent works just fine
with ZeroMQ as the eventloop, but barfs when using curl_httpclient.
