# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-17 11:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('team', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_of_licence', models.IntegerField(default=0, verbose_name='Number of licence')),
                ('price', models.FloatField(default=0.0)),
                ('currency', models.CharField(max_length=100)),
                ('payment_mathod', models.CharField(choices=[('paypal', 'PayPal'), ('wire', 'Wire Transfer')], default='paypal', max_length=20, verbose_name='Payment Method')),
                ('status', models.CharField(choices=[('quote', 'Quote'), ('paid', 'Paid'), ('cancel', 'Cancel')], max_length=20)),
                ('invoice', models.FileField(upload_to='invoice/')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.Team')),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
            },
        ),
        migrations.CreateModel(
            name='OrderRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_of_licence', models.IntegerField(default=0, verbose_name='Number of licence')),
                ('preferred_payment_mathod', models.CharField(choices=[('paypal', 'PayPal'), ('wire', 'Wire Transfer')], default='paypal', max_length=20, verbose_name='Preferred Payment Method')),
                ('message', models.TextField(blank=True)),
                ('response', models.CharField(max_length=1000)),
            ],
            options={
                'verbose_name': 'Order Request',
                'verbose_name_plural': 'Orders Request',
            },
        ),
    ]
