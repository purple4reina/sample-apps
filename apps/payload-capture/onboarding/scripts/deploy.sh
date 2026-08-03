#!/bin/bash -e
# Deploy the stack.
#
# Usage (run under your AWS credentials, e.g. `aweserv npm run deploy`):
#   scripts/deploy.sh

if [ -z "$DD_API_KEY" ]; then
  echo "❌ DD_API_KEY is not set. Export your Datadog API key before deploying." >&2
  exit 1
fi

# Pinned to the project's local CDK CLI so this can't silently fall back to
# an incompatible global install (see the CDK-CLI-vs-library mismatch this
# fixes: a bare `cdk` on PATH may resolve to an older global install).
npx --no-install cdk deploy
