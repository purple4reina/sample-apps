## Docker
Run a new container:

```bash
$ docker run -d -e C_FORCE_ROOT=true -v /Users/rabolofia/Documents/celery_app:/data celery
```

This will add everything in the celery_app directory as a mounted volume to the
container, meaning that any changes made locally will also show up immediately
in the container :)

The C_FORCE_ROOT environment variable will allow you to run celery workers as
root. Celery doesn't like this but I don't care.

Any further commands should be run with the "guest" user, for example:

```bash
docker exec -it --user guest <container sha> bash
```

+ Running celery: docker run -d -v $PWD:/data --net=host -p 5000:5000 celery
+ Running rabbitmq: docker run -d --net=host -p 5672:5672 rabbitmq

## Celery daemon

+ Running worker: C_FORCE_ROOT=true NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program celery worker -A tasks --concurrency=1 -l info -D
