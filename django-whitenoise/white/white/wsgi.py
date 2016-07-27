"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os

from newrelic.api.web_transaction import wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "white.settings")

from whitenoise.django import DjangoWhiteNoise

from django.core.wsgi import get_wsgi_application
# Wrap regular django wsgi app with DjangoWhiteNoise to server static
application = DjangoWhiteNoise(get_wsgi_application())
application = wsgi_application()(application)
