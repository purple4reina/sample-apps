#!/bin/bash -e

gradle build
aws-vault exec serverless-sandbox-account-admin -- serverless deploy
