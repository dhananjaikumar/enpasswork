# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-16 11:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp', '0002_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='force_password_change',
            field=models.BooleanField(default=True),
        ),
    ]