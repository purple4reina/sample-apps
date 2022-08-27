#!/bin/bash -e
aws-vault exec sandbox-account-admin -- sls deploy --region sa-east-1
