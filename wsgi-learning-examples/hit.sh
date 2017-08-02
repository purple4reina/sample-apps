#!/bin/bash


for i in {1..10}
do
    echo Starting $i
    curl http://192.168.59.103:8000 &

done

echo Done
