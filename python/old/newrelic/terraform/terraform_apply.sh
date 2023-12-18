#!/bin/bash

# Build and package the agent from the python_agent directory
rm -rf function/newrelic*
cd $PYAGENT_DIR
rm -rf dist
./build.sh
result=$?
cd -

if [[ $result != 0 ]]
then
    exit $result
fi

# Install the agent into the function/ directory without c-ext
NEW_RELIC_EXTENSIONS=false \
    pip install $PYAGENT_DIR/dist/newrelic-*.tar.gz -t function/ -U

# Unset any AWS environment variables
for e in $(env | grep AWS | tr '=' ' ' | awk '{print $1}')
do
    unset $e
done

# Run terraform apply
AWS_PROFILE=pdx_datacenter/okta_pythonagentteam terraform apply
