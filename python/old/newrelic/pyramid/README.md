# Pyramid

https://newrelic.zendesk.com/agent/tickets/223784


## Simple app

To run the super simple app, just do `python app.py`.


## The more complex option

Since the ticket included Mongo and started the server using `pserver`, I
wanted to attempt to recreate this.

In the `MyProject` directory is a sample application that was created using the
`pcreate` command. It has three different endpoints:

1. `/`: just returns a string `*`.
1. `/home`: renders a template and produces some fancy magic page.
1. `/mongo`: make a call to the mongo server and print the results.


### Starting

To start the more complex option, run `./docker/startapp.sh`. This will use
docker-compose to bring up both the mongo and pyramid containers.

The script `./docker/start_server.sh` will be run as the startup command on the
pyramid container. It first does a `pip install -e .` so that the pyramid code
is packaged correctly. Then it runs `pserve` through the `newrelic-admin`
script.


### Give it traffic

Included is a little script to hit the pyramid server. Running
`./docker/exercise_server.sh` will hit the `/mongo` endpoint once a second.


## Conclusions

I have not yet been able to recreate the customer's error.
