"""
Good morning Nathan, let me give some more details:

1. How does authentication work for your app? The pip freeze shows a
mozioinc/django-mozio-auth-client package and this application shows a
dependency in service maps on your Mozio Auth Appserver. We're particularly
interested in what happens when a user does not have permissions and if there
are any redirects involved.

From a high level view this endpoint uses DjangoRestFramework's
rest_framework.authentication.TokenAuthentication so every request must include
a header looking like `Authorization: Token
9944b091c9c62bcf9418ad846dd0e4bbdfc6ee4b` to be accepted.

If a request doesn't have this header or if the token is not valid, the
framework returns a 401 Unauthorized error.  Specifically it raises one of this
exceptions
https://github.com/tomchristie/django-rest-framework/blob/3.3.3/rest_framework/authentication.py#L177
that uses this details for status and messages:
https://github.com/tomchristie/django-rest-framework/blob/3.3.3/rest_framework/exceptions.py#L87
To check if the token is valid we perform a request to the Mozio Auth Appserver
(which also has NewRelic on it)

2. How is this view called? For example, is the page loaded with Ajax?
Additionally, it would be helpful to see the class declaration for the
LocationAreaViewSet.

We are calling this view directly at its /airport_checking/ endpoint from our
main app. This is the code that performs the calls from our main app:
"""

import urlparse
import requests
from requests.exceptions import Timeout
from django.conf import settings

def get_airport_data(lat=None, lng=None, timeout=None):
    endpoint_url = urlparseb.urljoin(settings.GATEWAY_LOCATION_AREAS_ENDPOINT, 'airport_checking/')
    headers = {'Authorization': 'TOKEN {}'.format(settings.GATEWAY_DE_TOKEN)}
    try:
        response = requests.get(endpoint_url, {'lat': lat, 'lng': lng}, headers=headers, timeout=timeout)
        if response.ok:
            data = response.json()
            return data
    except Timeout:
        return None

"""
There's nothing really interesting in the LocationAreaViewSet, just declaring
what queryset to use, what serializer, and such:
"""

class LocationAreaViewSet(BaseTrackViewSet):
    """
    ViewSet for the LocationArea model.
    """
    queryset = LocationArea.objects.all()
    serializer_class = LocationAreaSerializer
    search_fields = ('name', 'iata_code', 'icao_code')
    filter_backends = (SearchIATAFilter, DjangoFilterBackend, OrderingFilter)
    filter_fields = ('location_type', 'provider', 'iata_code', 'icao_code')
    ordering_fields = ('name', 'iata_code')

"""
3. How does redis caching work? We see the decorator
@cache(cache_key=get_point_cache_key, expires_in=CacheExpiryTime.ONE_YEAR) but
it's not something we're familiar with it. Where is this decorator defined and
how is it imported?

This decorator receives a function `get_point_cache_key` that builds a string
to use as key in Redis. The key looks like
"""

def get_point_cache_key(cls, lng, lat):
    """
    Build the cache key for the get_airport_by_point function.
    """
    return 'is_airport({lng}_{lat})'.format(lng=lng, lat=lat)

"""
The decorator itself is defined in one of the dependencies `mozio-commons` and
imported with
"""

from mozio_commons.cache.decorators import cache

"""
what it does is pickle the returned value from the function it decorates using
the provided `cache_key` and sets the expirity time for the value to that set
by the `expires_in` argument.

Hope this helps,
Regards.
"""
