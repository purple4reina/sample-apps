# Importing Zipped Packages

This sample application shows that you can import python packages that are
zipped and tests that we still instrument those packages.

Included files:

+ `requests.zip`: This is a zipped version of the requests library at v2.18.4.
  I created it as follows from inside a cloned version of the requests repo.

  ```bash
  $ python setup.py build
  $ cd build/lib
  $ zip requests requests/*
  ```

+ `app.py`: This is a simple app that imports the zipped requests library and
  makes a get to example.com. To confirm the agent instrumented things
  correctly, watch the audit.log for `example.com`.
