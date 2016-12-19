from django.conf.urls import url

from earth_view import EarthView
from mars_view import MarsView

urlpatterns = [
    url(r'^earth/', EarthView.as_view()),
    url(r'^mars/', MarsView.as_view()),
]
