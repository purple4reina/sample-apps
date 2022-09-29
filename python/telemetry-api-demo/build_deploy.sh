#!/bin/bash

PACKAGE_DIR=.package
SCRIPT_DIR=$(pwd)

echo "📦 packaging release"
echo

rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR/extensions
mkdir -p $PACKAGE_DIR/python_example_telemetry_api_extension

cp -r extensions/python_example_telemetry_api_extension $PACKAGE_DIR/extensions
cp -r extensions/*.py $PACKAGE_DIR/python_example_telemetry_api_extension

pip3 install \
    -r requirements.txt \
    -t $PACKAGE_DIR/python_example_telemetry_api_extension/

cd $PACKAGE_DIR

chmod 755 python_example_telemetry_api_extension/extension.py
chmod 755 extensions/python_example_telemetry_api_extension

zip -r extension.zip extensions python_example_telemetry_api_extension

cd $SCRIPT_DIR

echo
echo "🚀 deploying package"
aws-vault exec sandbox-account-admin -- sls deploy

echo
echo "🎉 deploy complete at $(date)"
