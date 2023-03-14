#!/bin/bash -e

echo "📦 packaging release"
echo
rm -rf .package
dotnet lambda package --configuration Release --output-package .package/handler.zip
echo
echo "🚀 deploying package"
sls deploy
echo
echo "🎉 deploy complete at $(date)"
