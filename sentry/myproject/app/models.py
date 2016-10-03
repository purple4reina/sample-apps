from django.db import models

class Wiggle(models.Model):

    @classmethod
    def get_wiggle_count(cls):
        return cls.objects.count()
