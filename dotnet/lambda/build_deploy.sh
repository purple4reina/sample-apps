#!/bin/bash -e

time (
  dotnet lambda package --configuration Release --output-package ./handler.zip
  aws-vault exec sandbox-account-admin -- sls deploy
)
