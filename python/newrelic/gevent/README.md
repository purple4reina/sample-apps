# Gevent

https://newrelic.zendesk.com/agent/tickets/228963


## Running

```
docker build --no-cache -it myapp --build-arg python=$PYTHON_VERSION . && docker run -it myapp
```

Where `$PYTHON_VERSION` is the version of python you want to use for the app.

To send traffic to it, run

```
docker exec -it $SHA /app/hitter.sh
```

Where `$SHA` is the container id of the new container.


## The Problem

When using python3.6, this app gives a `RecursionError: maximum recursion depth
exceeded` when trying to connect to the collector.
