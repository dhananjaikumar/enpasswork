# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-24 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orderinfo', '0017_auto_20170124_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrequest',
            name='order_id',
            field=models.CharField(default='262036381857941', editable=False, max_length=20, unique=True, verbose_name='Order Id'),
        ),
    ]