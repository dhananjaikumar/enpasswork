# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-24 09:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orderinfo', '0009_order_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='no_of_licence',
            field=models.PositiveIntegerField(default=0, verbose_name='Number of licence'),
        ),
        migrations.AlterField(
            model_name='order',
            name='price',
            field=models.FloatField(default=0.0, verbose_name='Net amount'),
        ),
    ]
