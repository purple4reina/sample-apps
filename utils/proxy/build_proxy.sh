#!/bin/bash -e

if [[ -z $ARCHITECTURE ]]; then
    ARCHITECTURE=amd64
fi

GOOS=linux GOARCH=$ARCHITECTURE go build -o extensions/proxy-extension main.go
zip -rq ext.zip extensions/proxy-extension
