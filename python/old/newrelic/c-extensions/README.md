# Importing C-Extensions

This is an example c-extension (borrowed and updated from
https://gist.github.com/physacco/2e1b52415f3a964ad2a542a99bebed8f) to
test our import hooks when used on a c module.

Included is a c-extension called "bottle". The choice was deliberate. I wanted
a name that would ensure that our instrumentation hooks would fire.

To install the c-extension:

```bash
$ pip install -e .
```

Then, run the test with

```bash
$ python app.py
```

The expected output will include an instrumentation error like:

```
2018-05-18 16:14:04,665 (45428/MainThread) newrelic.config ERROR - INSTRUMENTATION ERROR
2018-05-18 16:14:04,665 (45428/MainThread) newrelic.config ERROR - Type = import-hook
2018-05-18 16:14:04,666 (45428/MainThread) newrelic.config ERROR - Locals = {'instrumented': {('newrelic.hooks.framework_bottle', 'instrument_bottle')}, 'target': <module 'bottle' from '/Users/rabolofia/Documents/sample-apps/c-extensions/bottle.cpython-36m-darwin.so'>, 'module': 'newrelic.hooks.framework_bottle', 'function': 'instrument_bottle'}
2018-05-18 16:14:04,666 (45428/MainThread) newrelic.config ERROR - Exception Details
Traceback (most recent call last):
  File "/Users/rabolofia/Documents/python_agent/newrelic/config.py", line 1081, in _instrument
    function)(target)
  File "/Users/rabolofia/Documents/python_agent/newrelic/hooks/framework_bottle.py", line 125, in instrument_bottle
    framework_details = ('Bottle', getattr(module, '__version__'))
AttributeError: module 'bottle' has no attribute '__version__'
```

However, the c-extension should still load as normal and "Hello, world!" will
be printed to the screen.
