# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dumbapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dumbo',
            name='name',
            field=models.CharField(max_length=150),
        ),
    ]
