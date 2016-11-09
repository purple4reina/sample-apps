#!/bin/bash

test_mysql()
{
    host=$1
    mysql -h $host -ppython_agent -upython_agent -e ";" > /dev/null 2>&1
}

echo -n Waiting for mysql to be ready.

while true
do
    test_mysql mysql_one
    test_mysql mysql_two

    if [[ $? == 0 ]]
    then
        break
    fi

    echo -n .
    sleep 1
done

echo Ready

echo Installing local version of agent code
pip install -e /agent

$@
