## What is this project?

This project is a demonstration of an issue where spans are missing in AWS Lambda function, which is implemented in Rust
and packaged as a Docker image.
When invoked, it should generate a span for the invocation, the handler function, and a pseudo-processing function (with
five outer and inner spans each)
, totaling 27 (1 + 1 + 5 * 5) spans.

## How to package the project as Docker image

To package this project as a Docker image, execute the following command: (For Mac M1)

```bash
docker buildx build --build-context messense/rust-musl-cross:arm64-musl=docker-image://messense/rust-musl-cross:aarch64-musl --file ./Dockerfile --platform linux/arm64 --tag ${TAG_TO_PUSH_TO_ECR} .
docker pushd ${TAG_TO_PUSH_TO_ECR}
``` 

Ensure you replace ${TAG_TO_PUSH_TO_ECR} with the tag you intend to push to your ECR registry.

## How to run the app

To run the application on AWS Lambda:

1. Deploy the Docker image to AWS Lambda, ensuring that you select the arm64 architecture.

2. Configure the following environment variables in the Lambda function:

- `DD_API_KEY`
- `DD_ENV`
- `DD_OTLP_CONFIG_RECEIVER_PROTOCOLS_GRPC_ENDPOINT`: Set this as `localhost:4317`
- `DD_TRACE_OTEL_ENABLED`: Set this as `true`
- `DD_SERVERLESS_FLUSH_STRATEGY`: Set this as `end`
- `SAMPLING_RATIO`: sampling rate for the traces
- `SERVICE_NAME`: name of the service
- `URL`: URL of the receiver of otlp payload, sent from the application

3. Invoke the Lambda function using the Test Event feature in the AWS Console. Select the apigateway-http-api-proxy
   template to generate the test event for invoking the function.
