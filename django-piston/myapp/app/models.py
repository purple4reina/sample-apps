from django.db import models


class Cat(models.Model):
    color = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
