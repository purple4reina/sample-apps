# FastAPI

Quick start guide: https://fastapi.tiangolo.com/

## Google Cloud Run

+ Using project `datadog-sandbox`
+ Service name `rey-fastapi-test`
+ Region `us-west2`
+ Quick start guide: https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service

Deploy with
```bash
$ gcloud run deploy rey-fast-api --update-env-vars=DD_API_KEY=$DD_API_KEY --update-env-vars=DD_TRACE_ENABLED=true --update-env-vars=DD_SITE='datadoghq.com' --allow-unauthenticated
```

## AWS Lambda

Deploy with
```bash
$ aweserv sls deploy
```
