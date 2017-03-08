from django.db import models
from django.conf import settings


from products.models import Product, Variation


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    items = models.ManyToManyField(Variation)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class CartPosition(models.Model):
    pass