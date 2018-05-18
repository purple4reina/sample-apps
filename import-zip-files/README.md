# Importing Zipped Packages

This sample application shows that you can import python packages that are
zipped and tests that we still instrument those packages.

Included files:

+ `_mymodule.py`: This is the python module that is to be zipped. It has one
  method `fetch` that uses `requests` to get a url and return its response.
  Using `requests` is helpful because it allows us to know if our
  instrumentation has fired or not.
+ `mymodule.zip`: This file was created with this command on my mac: `zip
  mymodule mymodule.py`. Note the change in name of `_mymodule.py` which needs
  to be done again if you are going to rezip that file.
+ `app.py`: The app to run. Use it just with `python app.py`. It inserts the
  zip file into the path, initializes the agent, then uses the `fetch` method
  imported from `mymodule`. If all goes well, you'll see metrics for requests
  made to example.com.
