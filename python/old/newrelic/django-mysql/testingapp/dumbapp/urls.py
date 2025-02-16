from django.conf.urls import include, url

import views


urlpatterns = [
    url(r'^create_many/(?P<number>\w+)/$', views.create_many),
    url(r'^delete_all/$', views.delete_all),
    url(r'^hit/$', views.hit),
    url(r'^go_away/$', views.go_away),
    url(r'^latency/(?P<latency>\w+)/$', views.latency_connection),
    url(r'^latency/$', views.latency_connection),  # uses default latency value
]
