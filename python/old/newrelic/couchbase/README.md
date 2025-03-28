# Couchbase

This sample app is going to be used for our [Datastore API
MMF](https://newrelic.atlassian.net/browse/PYTHON-2306). We do not currently
instrument couchbase, so this package will be a good testing device for
learning more about how to use our current API.


## Running Couchbase

Use the provided `start_couchbase.sh` and `stop_couchbase.sh` scripts. This
will run couchbase in a docker container.

After starting the service, go to http://<DOCKER_IP>:8091 to setup your server.
_This is really important and must be done each time you start the service!_
Just run quickly through the quick start and select the default options. You
can get the ip of your docker vm by doing `echo $DOCKER_HOST`.


## Sample app

The sample app will connect to the `default` couchbase bucket and add and read
stuff from it.

You will also need the code from my `utils.decorators` module in order to get
the nicely printed transaction trace. If you don't want it, just comment it
out.

Be sure to replace your license key in the `newrelic.ini` file. I don't want
your stuff in my account.

Run the app my doing `python app.py`. Enjoy!
