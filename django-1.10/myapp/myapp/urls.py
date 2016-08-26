from django.conf.urls import url

import helloworld.views

urlpatterns = [
    url(r'^$', helloworld.views.index),
]
