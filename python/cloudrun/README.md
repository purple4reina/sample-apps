# python cloudrun

## Deploying

See https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-nodejs-service

```
$ gcloud run deploy rey-python-cloudrun --project datadog-sandbox --source . --update-env-vars=DD_API_KEY=$DD_API_KEY
```

Change region with

```
$ gcloud config set run/region <REGION>
```

Use project `datadog-serverless-gcp-dev` if you need to see logs.  They don't
currently seem to be working for the `datadog-sandbox` project.

## Invoking

Start the gcloud proxy: (https://docs.cloud.google.com/run/docs/authenticating/developers)

> The easiest way for you to test private services is to use the Cloud Run
> proxy in Google Cloud CLI. This proxies the private service to
> http://localhost:8080 (or to the port specified with --port), providing the
> token of the active account or another token you specify. This lets you use a
> web browser or a tool like curl. This is the recommended way to test
> privately a website or API in your browser.

```
$ gcloud run services proxy rey-python-cloudrun --project datadog-sandbox
```

Then, just curl localhost

```
$ curl http://localhost:8080
```
