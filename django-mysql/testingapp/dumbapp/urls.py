from django.conf.urls import include, url

import views


urlpatterns = [
    url(r'^create_many/(?P<number>\w+)/$', views.create_many),
]
