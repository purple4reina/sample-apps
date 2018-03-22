# Squid

This sample application uses [Squid](http://www.squid-cache.org/) as a proxy
server with the agent. Squid can be used both as a proxy and a caching system.
This configuration disables the caching and just sets up squid as a proxy.

## Configuring and Running Squid

A Dockerfile is provided for building the squid proxy. Squid is just installed
using `apt-get` and then a configuration file is added and the server is
started.

```
docker build -t squid .
```

You'll want to forward ports and networking so you can access the proxy from
your localhost (not inside a docker container).

```
docker run -it -p 3128:3128 --network=bridge squid
```

To determine the IP to use for accessing squid, find your docker host IP

```
echo $DOCKER_HOST
```

You'll now be able to test the proxy to `example.com` with

```
curl http://example.com --proxy 192.168.99.100:3128
```

It can take a request or two before squid is "ready". In the meantime, your
requests won't work. Try the `curl` command a couple of times in a row until
squid is "warmed up".

The output from squid is set to very verbose, but you should be able to see a
lot of details on each request it handles.


## Adding the agent

Now we'll configure the agent to use the squid proxy. There are a couple of
things to add to the `newrelic.ini` file to get this set up

```
proxy_host = 192.168.99.100
proxy_port = 3128
proxy_scheme = http
```

Be sure to set the `proxy_host` value to your docker host's actual IP. The
`proxy_scheme` value is also required.

Now run the agent test with `python background.py`. You will see the agent
working as it did before but, in the logs from your squid container you will
now be able to see traffic logged which indicates that the proxy is indeed
being used!


### Not All Endpoints Use the Proxy

For some reason you will only see 4-5 requests being handled by the squid proxy
for each time you run `python background.py`. This is very odd because the
agent will talk to the New Relic backend at least 9 times. I worried at first
that I had configured something incorrectly, but I ran the same test using
toxiproxy and got the same results. I have yet to be able to determine why some
endpoints go through the proxy and some do not.
