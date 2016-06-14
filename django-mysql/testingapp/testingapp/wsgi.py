"""
WSGI config for testingapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

import toxiproxy_controller

from django.core.wsgi import get_wsgi_application

# enable toxiproxy, this needs to be done before the server runs
if False:
    print 'setting up toxiproxy...'
    toxiproxy_controller.enable_latency()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testingapp.settings')

application = get_wsgi_application()
