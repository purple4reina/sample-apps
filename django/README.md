# A Simple Django App
Use freely and funly (is that even a word?)

## WSGI
See [tom's repo](https://source.datanerd.us/toffermann/wsgi_hello_world) about
wsgi for more stuff!

### gunicorn
From inside the myapp directory: `gunicorn myapp.wsgi`. Notice the dots to
represent the module paths.

### mod_wsgi
From inside the myapp directory: `mod_wsgi-express start-server myapp/wsgi.py
--debug-mode` the --debug-mode allows print statements to show up in the
console.

### uwsgi


## Python Agent
I put this line in the wsgi.py file `newrelic.agent.initialize('myapp/newrelic.ini')` so now I don't have to use the cmdline executable to get the agent going.
