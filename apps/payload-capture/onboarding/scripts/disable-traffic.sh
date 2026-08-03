#!/bin/bash -e
# Turn off the producer's schedule. No new orders are emitted, but anything
# already on the queue still drains through the processor.
#
# Usage (run under your AWS credentials, e.g. `aweserv npm run off`):
#   scripts/disable-traffic.sh

# Must match the region in bin/onboarding.ts. Set explicitly so an ambient
# AWS_REGION (e.g. from aws-vault) can't send this to the wrong region.
export AWS_REGION="sa-east-1"
RULE_NAME="rey-storefront-producer-schedule"

aws events disable-rule --name "$RULE_NAME" --region "$AWS_REGION"

echo "✅ traffic OFF ($RULE_NAME in $AWS_REGION) — no new orders will be emitted."
echo "   anything already on rey-storefront-orders-queue still drains normally."
