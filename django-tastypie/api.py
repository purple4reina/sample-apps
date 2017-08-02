from tastypie.resources import ModelResource
from tastypie.exceptions import NotFound
from django.contrib.auth.models import User


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'

    def get_detail(self, request, **kwargs):
        response = super(UserResource, self).get_detail(request, **kwargs)
        if response.status_code == 404:
            raise NotFound('I am raising an error!')
        return response
