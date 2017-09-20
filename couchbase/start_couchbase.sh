#!/bin/bash -e

docker run -d --name couchbase -p 8091-8094:8091-8094 -p 11210:11210 couchbase
