# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-14 13:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20170614_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='user_checkout',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.UserCheckout'),
        ),
    ]
