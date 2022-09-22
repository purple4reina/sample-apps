#!/bin/bash -e

time (
  echo "📦 packaging release"
  echo
  dotnet lambda package --configuration Release --output-package .package/handler.zip
  echo
  echo "🚀 deploying package"
  aws-vault exec sandbox-account-admin -- sls deploy
  echo
  echo "🎉 deploy complete at $(date)"
)
