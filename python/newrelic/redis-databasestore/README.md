# Redis Databasestore

1. Build docker image

```
docker build -t redis-app .
```

2. Run the app

```
docker run -it -v $PWD:/data redis-app
```

Since the app is mounted as a volume, the only time the image needs to be
rebuild is when the `requirements.txt` file changes.

Note that things may fail because the `REDIS_HOST` is wrong. I found this value
by running one of the redis tests using packnsend and seeing what host was
being used there.
