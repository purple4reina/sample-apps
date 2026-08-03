#!/bin/bash -e
# Turn on the producer's schedule (1/minute), producing continuous sample
# traffic without needing to redeploy.
#
# Usage (run under your AWS credentials, e.g. `aweserv npm run on`):
#   scripts/enable-traffic.sh

# Must match the region in bin/onboarding.ts. Set explicitly so an ambient
# AWS_REGION (e.g. from aws-vault) can't send this to the wrong region.
export AWS_REGION="sa-east-1"
RULE_NAME="rey-storefront-producer-schedule"

aws events enable-rule --name "$RULE_NAME" --region "$AWS_REGION"

echo "✅ traffic ON ($RULE_NAME in $AWS_REGION) — producer runs every minute."
echo "   note: redeploying the stack resets this rule back to disabled."
