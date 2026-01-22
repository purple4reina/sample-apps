# node cloudrun

See https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-nodejs-service

```
$ gcloud run deploy rey-python-cloudrun --allow-unauthenticated --project datadog-sandbox --source . --update-env-vars=DD_API_KEY=$DD_API_KEY
```

Change region with

```
$ gcloud config set run/region <REGION>
```
