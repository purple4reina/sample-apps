# Transaction Naming

This directory contains two separate apps to demonstrate the bad python 3
transaction naming issue.

## Django

https://newrelic.atlassian.net/browse/PYTHON-1891

In this use case, the views are class based views that are inherited.

Run the server

```
newrelic-admin run-program python3 django_app/manage.py runserver
```

Send it traffic

```
while true
do
    sleep 1
    curl http://localhost:8000/earth/
    curl http://localhost:8000/mars/
    curl http://localhost:8000/tri/
done
```
