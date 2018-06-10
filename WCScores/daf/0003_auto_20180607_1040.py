# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-07 10:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WCScores', '0002_auto_20180606_2206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='FIFA',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='country',
            field=models.CharField(max_length=16, unique=True),
        ),
    ]