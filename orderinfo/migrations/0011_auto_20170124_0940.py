# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-24 09:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orderinfo', '0010_auto_20170124_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrequest',
            name='no_of_licence',
            field=models.PositiveIntegerField(default=0, verbose_name='Number of licence'),
        ),
    ]
