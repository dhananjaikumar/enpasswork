# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-23 10:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orderinfo', '0006_auto_20170123_0942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='reason',
            field=models.TextField(blank=True, verbose_name='Reason for cancellation'),
        ),
    ]
