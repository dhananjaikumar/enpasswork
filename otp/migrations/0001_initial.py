# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-17 11:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Otp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('one_time_password', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expired', models.BooleanField(default=False)),
                ('teamuser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='team.TeamUser')),
            ],
        ),
    ]