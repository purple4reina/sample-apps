# Request Queueing

This sample app is to demonstrate request queueing using nginx and uwsgi as per https://newrelic.zendesk.com/agent/tickets/211196 support ticket. At the time of this writing, request queueing (and the actual serving of the wsgi app entirely) has yet to be successfully configured.

+ Build the docker image with `docker build -t mynginx .`
+ Run the container with `docker run -it -p 80:80 mynginx`
+ To hit the server, you'll need to ip of the docker host. Find that with `echo $DOCKER_HOST`
+ Repeatedly curl the page `while true ; do curl http://<docker-host> ; sleep 1 ; done`

I wish I could give better details, but this isn't working so great right now.
