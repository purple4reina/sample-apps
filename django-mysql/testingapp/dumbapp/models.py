from django.db import models


class Dumbo(models.Model):
    name = models.CharField(max_length=150)
