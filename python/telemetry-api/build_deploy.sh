#!/bin/bash

PACKDIR=.package

echo "📦 packaging release"
echo

mkdir -p $PACKDIR/extensions
mkdir -p $PACKDIR/python_example_telemetry_api_extension

chmod 755 extension/extension.py
pip3 install -r requirements.txt -t $PACKDIR/python_example_telemetry_api_extension/
chmod 755 extension/python_example_telemetry_api_extension

cp extension/python_example_telemetry_api_extension $PACKDIR/extensions
cp extension/*.py $PACKDIR/python_example_telemetry_api_extension
zip -r $PACKDIR/extension.zip $PACKDIR/extensions $PACKDIR/python_example_telemetry_api_extension

echo
echo "🚀 deploying package"
aws-vault exec sandbox-account-admin -- sls deploy

echo
echo "🎉 deploy complete at $(date)"
