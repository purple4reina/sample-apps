# uWSGI Segfaults

https://newrelic.atlassian.net/browse/PYTHON-2551 and https://github.com/unbit/uwsgi/issues/1651#issuecomment-336914171

This agent diff gets rid of the segfault

```diff
diff --git a/newrelic/core/agent.py b/newrelic/core/agent.py
index d2237b4..8c9a830 100644
--- a/newrelic/core/agent.py
+++ b/newrelic/core/agent.py
@@ -213,7 +213,8 @@ class Agent(object):
         self._lock = threading.Lock()

         if self._config.enabled:
-            atexit.register(self._atexit_shutdown)
+            pass
+            #atexit.register(self._atexit_shutdown)

             # Register an atexit hook for uwsgi to facilitate the graceful
             # reload of workers. This is necessary for uwsgi with gevent
@@ -225,16 +226,16 @@ class Agent(object):
             # append our atexit hook to any pre-existing ones to prevent
             # overwriting them.

-            if 'uwsgi' in sys.modules:
-                import uwsgi
-                uwsgi_original_atexit_callback = getattr(uwsgi, 'atexit', None)
+            #if 'uwsgi' in sys.modules:
+            #    import uwsgi
+            #    uwsgi_original_atexit_callback = getattr(uwsgi, 'atexit', None)

-                def uwsgi_atexit_callback():
-                    self._atexit_shutdown()
-                    if uwsgi_original_atexit_callback:
-                        uwsgi_original_atexit_callback()
+            #    def uwsgi_atexit_callback():
+            #        self._atexit_shutdown()
+            #        if uwsgi_original_atexit_callback:
+            #            uwsgi_original_atexit_callback()

-                uwsgi.atexit = uwsgi_atexit_callback
+            #    uwsgi.atexit = uwsgi_atexit_callback

         self._data_sources = {}
```

Ends up the segfault happens when making a request to the data collector. I was
able to reproduce the issue by just making a request call to
https://example.com. Notice that http://example.com does not segfault.

Additionally, notice that this issue only happens when run in docker. To
reproduce do:

```
$ docker build -t segfault .
$ docker run -it --network=bridge -p 8000:8000 segfault
```

Then exercise the application by curling the docker host:

```
$ echo $DOCKER_HOST
tcp://192.168.99.100:2376
$ curl http://192.168.99.100:8000
```

## Possible workarounds?

There are no actual workarounds that will fix this issue. It is something that
uwsgi must fix. Allan has opened a pull request to do so
https://github.com/unbit/uwsgi/pull/1879.

There is a way to get rid of the segfault, but customers will still lose all
data for the final harvest down as part of atexit.

1. Add the `--skip-atexit-teardown` option to uwsgi startup command
2. Remove the agent's uwsgi atexit callback with:

   ```python
    import newrelic.core.agent

    def remove_uwsgi_atexit():
        def noop_atexit():
            pass
        import uwsgi
        uwsgi.atexit = noop_atexit

    newrelic.core.agent.Agent.run_on_startup(remove_uwsgi_atexit)
    ```

    Do this **before** initializing or registering the agent.
