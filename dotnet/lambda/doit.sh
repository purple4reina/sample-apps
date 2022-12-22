#!/bin/bash -e

aws-vault exec serverless-sandbox-account-admin -- ./build_deploy.sh

echo
echo "🏏 hitting endpoint"
date

for _ in {1..5}
do
  curl https://ijeyqbzyj6sznpmx65676pzuji0wodrk.lambda-url.sa-east-1.on.aws
done

echo
echo
echo "✅ done!"
