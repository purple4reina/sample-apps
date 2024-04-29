#!/bin/bash

echo Starting! 🎬

DD_ENV=rey \
    DD_OTLP_CONFIG_RECEIVER_PROTOCOLS_HTTP_ENDPOINT=localhost:4318 \
    DD_LOG_LEVEL=debug \
        go run -tags "serverless otlp" ./cmd/serverless-init/ \
            ~/dd/sample-apps/python/otlp/env/bin/python ~/dd/sample-apps/python/otlp/handler.py \
        | grep --color=auto "Sending sketches payload"

echo Done! ⏱
