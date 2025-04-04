#!/bin/bash -e

./node_modules/.bin/esbuild \
    handler.ts \
        --bundle \
        --minify \
        --sourcemap \
        --platform=node \
        --target=es2020 \
        --external:datadog-lambda-js \
        --outfile=handler.js

aws-vault exec sso-serverless-sandbox-account-admin -- sls deploy
