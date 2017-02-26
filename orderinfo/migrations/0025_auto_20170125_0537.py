# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-25 05:37
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orderinfo', '0024_auto_20170125_0517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='no_of_licence',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number of licence'),
        ),
        migrations.AlterField(
            model_name='orderrequest',
            name='no_of_licence',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number of licence'),
        ),
        migrations.AlterField(
            model_name='orderrequest',
            name='order_id',
            field=models.CharField(default='628811950107862', max_length=20, unique=True, verbose_name='Order ID'),
        ),
    ]
