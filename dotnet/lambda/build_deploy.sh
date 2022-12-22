#!/bin/bash -e

echo "📦 packaging release"
echo
dotnet lambda package --configuration Release --output-package .package/handler.zip
echo
echo "🚀 deploying package"
sls deploy
echo
echo "🎉 deploy complete at $(date)"
