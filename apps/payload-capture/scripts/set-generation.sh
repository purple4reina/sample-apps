#!/bin/bash -e
# Set the upstream format generation the producer emits.
#
# Usage (run under your AWS credentials, e.g. `aweserv npm run drift`):
#   scripts/set-generation.sh [stable|next|scheme-case|datetime|counterparty]
#
# `npm run drift` -> next, `npm run heal` -> stable.

GENERATION="${1:-stable}"
export AWS_REGION="${AWS_REGION:-sa-east-1}"
PARAM_NAME="/rey/payload-capture/format-generation"

aws ssm put-parameter \
  --overwrite \
  --name "$PARAM_NAME" \
  --type String \
  --value "$GENERATION" \
  --region "$AWS_REGION" >/dev/null

echo "✅ upstream format generation set to '$GENERATION' ($PARAM_NAME in $AWS_REGION)"
echo "   new traffic reflects this within ~1 minute (next scheduled producer run)."
