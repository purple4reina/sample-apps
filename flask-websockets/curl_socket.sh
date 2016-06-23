#!/bin/bash -ex

path=$1
port=$2

if [ -n "$path" ]
then
    path=/${path}/
fi

curl -i -H "Connection: Upgrade" \
    -H "Upgrade: websocket" \
    -H "Host: localhost:${port}" \
    -H "Origin:http://localhost:${port}" \
    -H "Sec-WebSocket-Version: 13" \
    -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
    http://localhost:${port}${path}
