# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-12 22:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20170612_1513'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='shipping_cost',
            new_name='shipping_total',
        ),
    ]