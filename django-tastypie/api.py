from tastypie.resources import Resource
from tastypie.exceptions import NotFound
from django.contrib.auth.models import User


class UserResource(Resource):
    class Meta:
        resource_name = 'user'

    def obj_get(self, *args, **kwargs):
        raise NotFound()
