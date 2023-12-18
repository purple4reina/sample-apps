# Background Task

This is just a super simple background task. Nothing fancy.

## Data Source

Use this application to add a data source via config file. Add the following to
the `newrelic.ini` file:

```
[data-source:test-datasource]
enabled = true
function = datasource:test_datasource
name = MY_DATA_SOURCE
```

This will register the `test_datasource` method as a data source. I'm not
totally sure what it's suppose to do but it does it!
