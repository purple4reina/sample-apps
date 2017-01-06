# Mongo

https://newrelic.zendesk.com/agent/tickets/223784

Customer reported error when using the agent, but no error when not using
agent:

```
Traceback (most recent call last):
  File "/data/app.py", line 23, in <module>
    main()
  File "/data/app.py", line 18, in main
    unique=True, sparse=True)
  File "/data/customer_files/customer_file.py", line 47, in <lambda>
    return lambda *args, **kwargs: self._wrap(func, args, kwargs)
  File "/data/customer_files/customer_file.py", line 54, in _wrap
    result = reconnect(func)(self.other, *args, **kwargs)
  File "/data/customer_files/customer_file.py", line 17, in wrapper
    return func(*args, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/newrelic-2.76.0.55/newrelic/api/datastore_trace.py", line 77, in _nr_datastore_trace_wrapper_
    return wrapped(*args, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/pymongo/collection.py", line 1162, in ensure_index
    keys = helpers._index_list(key_or_list)
  File "/usr/local/lib/python2.7/dist-packages/pymongo/helpers.py", line 44, in _index_list
    raise TypeError("if no direction is specified, "
TypeError: if no direction is specified, key_or_list must be an instance of list
```

### To recreate
+ run app with the agent `USE_AGENT=True ./startapp.sh`
+ run app without the agent `USE_AGENT=False ./startapp.sh`

### Solution

They should replace

```python
if type(func) == MethodType:
```

with

```python
if inspect.ismethod(func):
```

in their code. The End.
