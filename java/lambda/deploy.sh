#!/bin/bash -e

./gradlew clean build
aws-vault exec serverless-sandbox-account-admin -- serverless deploy
