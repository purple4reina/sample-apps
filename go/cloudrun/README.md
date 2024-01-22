# node cloudrun

See https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-go-service

```
$ gcloud run deploy rey-go-cloudrun --allow-unauthenticated --project datadog-sandbox --source . --update-env-vars=DD_API_KEY=$DD_API_KEY
```
