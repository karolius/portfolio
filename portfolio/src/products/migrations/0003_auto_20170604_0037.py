# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-03 22:37
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20170519_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='media',
            field=models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='C:\\Repo\\portfolio\\portfolio\\static_in_env\\protected'), upload_to=products.models.download_media_location),
        ),
    ]
