# Opentelemetry on Google Cloud Run

deploy:

```bash
$ gcloud run deploy rey-otlp-gcp-node --update-env-vars=DD_API_KEY=$DD_API_KEY --allow-unauthenticated --source .
```
