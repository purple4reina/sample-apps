#!/bin/bash -e


# stop all currently running containers
echo
echo Stopping all containers
for each in `docker ps -a | grep -v CONT | awk '{print $1}'`
do
    echo Removing running container: $each
    docker rm -f $each
done

# make sure that there is no residual redis or postgres or sentry images
echo
echo Removing old redis images
for each in `docker images | grep redis | awk '{print $3}'`
do
    echo Removing image: $each
    docker rmi -f $each
done

echo
echo Starting redis
docker run -d \
    --name sentry-redis \
        redis

echo
echo Starting postgres
docker run -d \
    --name sentry-postgres \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_USER=sentry \
        postgres
sleep 5

echo
echo Updating Sentry
docker run -it --rm \
    -e SENTRY_SECRET_KEY='super-secret-key' \
    --link sentry-postgres:postgres \
    --link sentry-redis:redis \
        sentry upgrade

echo
echo Starting Sentry server
docker run -d \
    --name my-sentry \
    -e SENTRY_SECRET_KEY='super-secret-key' \
    --link sentry-redis:redis \
    --link sentry-postgres:postgres \
    -p 8080:9000 \
        sentry

echo
echo Starting the celery stuff
docker run -d \
    --name sentry-cron \
    -e SENTRY_SECRET_KEY='super-secret-key' \
    --link sentry-postgres:postgres \
    --link sentry-redis:redis \
        sentry run cron

docker run -d \
    --name sentry-worker-1 \
    -e SENTRY_SECRET_KEY='super-secret-key' \
    --link sentry-postgres:postgres \
    --link sentry-redis:redis \
        sentry run worker

echo
echo Sentry now available at http://192.168.99.100:8080
