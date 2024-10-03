#!/bin/bash -e

# build function code
JAVA_HOME=$JAVA_11_HOME gradle build

# build custom tracing layer
LAYER_ZIP="tracer.zip"
rm -rf layer
mkdir -p layer/java/lib
cp dd-java-agent-*.jar layer/java/lib/dd-java-agent.jar
cd layer
zip -r ../$LAYER_ZIP java
cd ..
rm -rf layer

aws-vault exec sso-serverless-sandbox-account-admin -- serverless deploy
