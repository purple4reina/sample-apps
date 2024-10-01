#!/bin/bash -e

JAVA_HOME=$JAVA_11_HOME gradle build
aws-vault exec serverless-sandbox-account-admin -- serverless deploy
