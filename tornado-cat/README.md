# Tornado CAT

https://source.datanerd.us/python-agent/python_agent/pull/548

Demonstrates the existence (or non existence) of CAT headers in responses.

## Server

This is a tornado 4 app with several endpoints. Start it with `newrelic-admin
run-python server.py`. Depending on the version of the agent, if receiving CAT
headers, it may or may not send CAT response headers.

## Client

This is a flask app that makes an external call to the tornado 4 server. The
response body it returns depends on if the New Relic CAT headers were found in
the external call headers. Start the client with `newrelic-admin run-python
client.py` then send it traffic to http://localhost:5000.

Understanding the response:

+ `+`: New Relic CAT headers found
+ `-`: New Relic CAT headers not found
+ `!`: Something went wrong when sending the external request
