# Cherrypy

## Support ticket

https://newrelic.zendesk.com/agent/tickets/224215

User reported an inability to ignore errors of status code 400. I was unable to
reproduce what they were seeing.


## SEGFAULT

When running this app using uwsgi as per the [cherry-py
docs](http://docs.cherrypy.org/en/latest/deploy.html#uwsgi), a SEGFAULT is hit.

To recreate, run `./start_app.sh`.
