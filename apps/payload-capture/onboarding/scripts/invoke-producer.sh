#!/bin/bash -e
# Fire a single producer run on demand (in addition to any scheduled runs).
#
# Usage (run under your AWS credentials, e.g. `aweserv npm run invoke`):
#   scripts/invoke-producer.sh

# Must match the region in bin/onboarding.ts. Set explicitly so an ambient
# AWS_REGION (e.g. from aws-vault) can't send this to the wrong region.
export AWS_REGION="sa-east-1"

aws lambda invoke \
  --region "$AWS_REGION" \
  --function-name rey-storefront-producer \
  --payload "$(echo '{"source":"manual"}' | base64)" \
  outfile.json >/dev/null

echo "✅ producer invoked:"
cat outfile.json
echo
