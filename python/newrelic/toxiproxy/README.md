# Toxiproxy

This sample application uses [Toxiproxy](https://github.com/Shopify/toxiproxy)
as a proxy server with the agent. Toxiproxy is a simple proxy server written in
Go that can be used to simulate bad network connections. By adding "toxics" to
Toxiproxy, you can add things like latency, connection timeouts, and bandwidth
limiting.

## Configuring and Running Toxiproxy

The `toxiproxy.json` file houses the configuration for the server. There are
currently three proxies set up: `collector.newrelic.com`,
`staging-collector.newrelic.com`, and `example.com`.

First off, you'll want to build the docker image

```
docker build -t toxiproxy .
```

Then start the proxy with

```
docker run -it -p 8474:8474 -p 22220-22222:22220-22222 --network=bridge toxiproxy
```

You will now be able to connect to the proxy from your localhost. You'll now be
able to test the proxy to `example.com` with

```
curl http://example.com --proxy localhost:22222
```

### Adding Toxics

The most useful toxic I've found is adding latency to the system. Toxiproxy has
a REST API served on port 8474 that allows you to add and configure toxics. For
more details, visit their [docs](https://github.com/Shopify/toxiproxy).

To add a latency toxic to the `example.com` proxy

```
curl -XPOST http://192.168.99.100:8474/proxies/example/toxics -d '{"type":"latency","attributes":{"latency":100}}'
```

The latency is in milliseconds. To now update this toxic to increase the
latency do

```
curl -XPOST http://192.168.99.100:8474/proxies/example/toxics/latency_downstream -d '{"type":"latency","attributes":{"latency":1000}}'
```

Now when you reach out to `example.com` again, it will take an added 1 second.


## Adding the Agent

Now we'll configure the agent to use Toxiproxy. There are a couple of things to
add to the `newrelic.ini` file to get this set up

```
proxy_host = 192.168.99.100
proxy_port = 22220

shutdown_timeout = 100
```

Be sure to set the `proxy_host` value to your docker host's actual IP. The
`shutdown_timeout` is necessary if you are adding latency to the system.

Now run the agent test with `python background.py`. You will see the agent
working as it did before but, in the logs from your Toxiproxy container you
will see things like

```
INFO[0261] Accepted client              client=192.168.99.1:62196 name=collector proxy=[::]:22220 upstream=collector.newrelic.com:443
WARN[0261] Source terminated            bytes=4000 err=read tcp 172.17.0.17:48970->50.31.164.146:443: use of closed network connection name=collector
```

which indicate that the proxy is indeed being used! The warning level logging
message can be ignored, because it seems that the round trip to the collector
is being completed as expected.

### Not All Endpoints Use the Proxy

For some reason you will only see 4-5 logging lines with `Accepted client` per
time you run `python background.py`. This is very odd because the agent will
talk to the New Relic backend at least 9 times. I worried at first that I had
configured something incorrectly, but I ran the same test using a squid proxy
and got the same results. I have yet to be able to determine why some endpoints
go through the proxy and some do not. You can determine which are actually
using the proxy by adding a small latency toxic and examining which calls from
`newrelic/core/data_collector.py` are taking the longest.
