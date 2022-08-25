#!/bin/bash -e

time (
  echo "📦 packaging release"
  dotnet lambda package --configuration Release --output-package ./handler.zip
  echo "🚀 deploying package"
  aws-vault exec sandbox-account-admin -- sls deploy
  echo "🎉 deploy complete at $(date)"
)
