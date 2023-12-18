from django.conf.urls import include, url

from testapp import views

urlpatterns = [
    url(r'^classbased1/$', views.ListViewExample.as_view()),
    url(r'^classbased2/$', views.TemplateViewExample.as_view()),
    url(r'^functionbased/$', views.FunctionViewExample),
]
