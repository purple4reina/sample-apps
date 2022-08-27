from django.conf.urls import include, url

import views


urlpatterns = [
    url(r'^shutdown/$', views.shutdown_agent),
]
