#!/bin/bash -e

if [[ -z $ARCHITECTURE ]]; then
    ARCHITECTURE=amd64
fi

echo "Building recorder extension"
cd recorder-extension
GOOS=linux GOARCH=$ARCHITECTURE go build -o extensions/recorder-extension main.go
zip -rq ext.zip extensions/recorder-extension
