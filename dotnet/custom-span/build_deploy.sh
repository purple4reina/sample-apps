#!/bin/bash -e

echo "📦 packaging release"
echo
rm -rf .package
dotnet lambda package --configuration Release --output-package .package/handler.zip
echo "🧹 removing tracer from package"
zip -d .package/handler.zip Datadog.Trace.dll
echo
echo "🚀 deploying package"
aws-vault exec sso-serverless-sandbox-account-admin -- serverless deploy
echo
echo "🎉 deploy complete at $(date)"
