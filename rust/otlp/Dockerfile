# syntax=docker/dockerfile:1.7
FROM --platform=linux/arm64 datadog/lambda-extension:55 as datadog_lambda_extension

# use --build-context messense/rust-musl-cross:arm64-musl=docker-image://messense/rust-musl-cross:aarch64-musl --build-context messense/rust-musl-cross:amd64-musl=docker-image://messense/rust-musl-cross:x86_64-musl
FROM --platform=$BUILDPLATFORM messense/rust-musl-cross:${TARGETARCH}-musl as builder

ARG TARGETARCH

RUN if [ $TARGETARCH = "amd64" ]; then \
      echo "x86_64" > /arch; \
    elif [ $TARGETARCH = "arm64" ]; then \
      echo "aarch64" > /arch; \
    else \
      echo "Unsupported platform: $TARGETARCH"; \
      exit 1; \
    fi

COPY ./Cargo.toml /
COPY ./Cargo.lock /
COPY src/main.rs /src/
RUN cargo build --release --target $(cat /arch)-unknown-linux-musl \
    && cp /target/$(cat /arch)-unknown-linux-musl/release/missing-span-sample /home/rust/bootstrap

FROM --platform=linux/arm64 public.ecr.aws/lambda/provided:al2

VOLUME /opt/extensions

COPY --from=datadog_lambda_extension /opt/extensions/datadog-agent  /opt/extensions/
COPY --from=builder /home/rust/bootstrap  ${LAMBDA_RUNTIME_DIR}/bootstrap
CMD [ "lambda-handler" ]
