#!/bin/bash -e
# Fire a single producer run on demand (in addition to the scheduled runs).
#
# Usage (run under your AWS credentials, e.g. `aweserv npm run invoke`):
#   scripts/invoke-producer.sh

export AWS_REGION="${AWS_REGION:-sa-east-1}"

aws lambda invoke \
  --region "$AWS_REGION" \
  --function-name rey-settlement-producer \
  --payload "$(echo '{"source":"manual"}' | base64)" \
  outfile.json >/dev/null

echo "✅ producer invoked:"
cat outfile.json
echo
