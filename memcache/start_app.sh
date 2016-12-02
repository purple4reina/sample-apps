#!/bin/bash

if [[ $1 == '--first-run' ]]
then
    docker-compose up --abort-on-container-exit --build
else
    docker-compose up --abort-on-container-exit
fi
