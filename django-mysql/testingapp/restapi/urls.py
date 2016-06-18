from django.conf.urls import include, url

import views


urlpatterns = [
    url(r'^go_away/$', views.GoAwayDumbo.as_view()),
    url(r'^go_away/noserial/$', views.GoAwayDumboNoSerializer.as_view()),

    # uses default latency (from toxiproxy_controller.LATENCY)
    url(r'^latency/$', views.LatencyConnection.as_view()),
    url(r'^latency/noserial/$', views.LatencyConnectionNoSerializer.as_view()),

    url(r'^latency/(?P<latency>\w+)/$', views.LatencyConnection.as_view()),
    url(r'^latency/noserial/(?P<latency>\w+)/$',
            views.LatencyConnectionNoSerializer.as_view()),

    url(r'^post/$', views.CreateDumbo.as_view()),
    url(r'^post/noserial/$', views.NoSerializer.as_view()),
]
