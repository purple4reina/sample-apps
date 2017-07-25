from django.conf.urls import url, include

import views

from api import UserResource

user_resource = UserResource()

urlpatterns = [
    url(r'^status/', views.Index.as_view()),
    url(r'^api/', include(user_resource.urls)),
]
