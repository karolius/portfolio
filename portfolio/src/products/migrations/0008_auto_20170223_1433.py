# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-23 13:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_productvariation'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductVariation',
            new_name='Variation',
        ),
    ]
