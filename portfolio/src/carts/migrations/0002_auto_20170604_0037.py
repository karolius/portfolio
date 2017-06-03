# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-03 22:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='tax_rate',
            field=models.DecimalField(decimal_places=2, default=0.23, max_digits=5),
        ),
    ]