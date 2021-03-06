# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-02-07 09:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orderinfo', '0026_auto_20170125_0635'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderrequest',
            options={'verbose_name': 'Purchase Order', 'verbose_name_plural': 'Purchase Orders'},
        ),
        migrations.AlterField(
            model_name='order',
            name='invoice',
            field=models.FileField(blank=True, upload_to='invoice', validators=['file_validator']),
        ),
    ]
