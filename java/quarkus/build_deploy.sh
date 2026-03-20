#!/bin/bash -e

quarkus build
sls deploy
