#!/bin/bash

test_mysql()
{
    mysql -h mysql -ppython_agent -upython_agent -e ";" > /dev/null 2>&1
}

echo -n Waiting for mysql to be ready.

while true
do
    test_mysql

    if [[ $? == 0 ]]
    then
        break
    fi

    echo -n .
    sleep 1
done

echo Ready

$@
