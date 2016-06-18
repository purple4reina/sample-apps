from rest_framework import serializers

from dumbapp.models import Dumbo


class DumboSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dumbo
        fields = ('name',)
