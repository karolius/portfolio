# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-05-18 15:55
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import products.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=25)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True)),
                ('sale_active', models.BooleanField(default=False)),
                ('media', models.ImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='C:\\Repo\\portfolio\\portfolio\\static_in_env\\protected'), upload_to=products.models.download_media_location)),
                ('status', models.CharField(choices=[('active', 'Active'), ('out_of_stock', 'Out of stock'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('category', models.ManyToManyField(blank=True, to='products.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('hd', 'HD'), ('sd', 'SD'), ('micro', 'Micro')], default='hd', max_length=12)),
                ('height', models.CharField(blank=True, max_length=10, null=True)),
                ('width', models.CharField(blank=True, max_length=10, null=True)),
                ('media', models.ImageField(blank=True, height_field='height', null=True, upload_to=products.models.thumbnail_location, width_field='width')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Variation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('sub_description', models.CharField(blank=True, max_length=360, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=25)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True)),
                ('sale_active', models.BooleanField(default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product')),
            ],
        ),
    ]
