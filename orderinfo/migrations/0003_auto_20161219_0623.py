# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-19 06:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orderinfo', '0002_orderrequest_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrequest',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='team.Team'),
        ),
    ]
