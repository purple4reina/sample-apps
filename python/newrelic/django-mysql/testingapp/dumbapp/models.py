import time

from django.db import models


class Dumbo(models.Model):
    name = models.CharField(max_length=150)

    @classmethod
    def create_name(name):
        return 'Dumbo %s' % time.time()
