#!/bin/bash -e

JAVA_HOME=$JAVA_11_HOME gradle build
aws-vault exec sso-serverless-sandbox-account-admin -- serverless deploy
