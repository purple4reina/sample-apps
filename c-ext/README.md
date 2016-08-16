# C-Extensions

A repo for [/Objects/tupleobject.c:156: bad argument to internal function](https://newrelic.atlassian.net/browse/PYTHON-2004)

Included directories:
1. `system-error-ticket`: Submodule for Tom's investigations, https://source.datanerd.us/toffermann/system-error-ticket
2. `NewRelic`: Module made by customer to demonstrate the bug, https://github.com/Mobeye/NewRelic
3. `application`: My reproduction


## Offending packages

There have been 6 support tickets filed related to this bug. Here is a reduction of the packages each is using.

##### https://newrelic.zendesk.com/agent/tickets/197263 - p2

+ Python 3.5.1+ (Ubuntu package version 3.5.1-10)
+ Django==1.9.7
+ newrelic==2.66.0.49
+ Uwsgi: 2.0.12-5ubuntu3

##### https://newrelic.zendesk.com/agent/tickets/183712 - p4

+ Python 3.5.1
+ Django==1.9.3
+ newrelic==2.60.0.46
+ uwsgi==2.0.12

##### https://newrelic.zendesk.com/agent/tickets/202961 - p5

+ Python 3.5.2
+ Django 1.9.7
+ newrelic 2.68.0.50
+ uwsgi 1.9.21 (but we also tried 2.0.13.1)

##### https://newrelic.zendesk.com/agent/tickets/203443 - p1

+ python3.5 3.5.1-10 amd64
+ Django==1.9.8
+ newrelic==2.66.0.49
+ uWSGI==2.0.13.1

##### https://newrelic.zendesk.com/agent/tickets/204918 - p2

+ Python 3.5
+ Django
+ newrelic
+ uwsgi

##### https://newrelic.zendesk.com/agent/tickets/205505 - p0

+ Python 3.5
+ Django (1.9.7)
+ newrelic (2.68.0.50)
+ uWSGI (2.0.13.1)

### What Fails

+ Django 1.9.6, Python 3.5.1, uWSGI 2.0.13.1, newrelic 2.60.0.46

### What Works

Alternate WSGI servers
+ Django 1.9.6, Python 3.5.1, newrelic 2.60.0.46, **mod-wsgi 4.5.2**
+ Django 1.9.6, Python 3.5.1, newrelic 2.60.0.46, **gunicorn 19.6.0**

Previous Django version
+ **Django 1.8.13**, Python 3.5.1, newrelic 2.60.0.46, uWSGI 2.0.13.1

Python 2.7 and 3.4 or pervious
+ Django 1.9.6, **Python 2.7.11**, newrelic 2.60.0.46, mod-wsgi 4.5.2
