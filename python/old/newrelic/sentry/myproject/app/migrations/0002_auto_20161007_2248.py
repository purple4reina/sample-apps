# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-07 22:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='wiggle',
            name='location_type',
            field=models.IntegerField(default=123),
        ),
        migrations.AddField(
            model_name='wiggle',
            name='name',
            field=models.CharField(db_index=True, default=123, max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wiggle',
            name='osm_id',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='wiggle',
            name='osm_type',
            field=models.CharField(choices=[(b'r', b'relation'), (b'w', b'way'), (b'n', b'node')], max_length=1, null=True),
        ),
    ]
