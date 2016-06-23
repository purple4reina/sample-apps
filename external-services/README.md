# Testing external services
https://newrelic.zendesk.com/agent/tickets/198673

Customer reported issue where in a non instrumented external service (googleads)
which called an instrumented external service (urllib), the urllib transactions
were not showing up in the External Services tab.

## Setup

1. Setup virtualenv and source it

```
virtualenv env
source env/bin/activate
```

2. Create small non instrumented package by moving a file to site-packages.

```
cp mytest_package.py env/lib/python2.7/site-packages/
```

3. Make sure you have newrelic!

```
pip install newrelic
```

4. Update the `newrelic.ini` file to use your license key.

5. Run the task

```
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-python run_background_task.py
```
