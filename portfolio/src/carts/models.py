from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.urls import reverse

from products.models import Variation, Product


class CartItem(models.Model):
    cart = models.ForeignKey("Cart")
    variation = models.ForeignKey(Variation)
    quantity = models.IntegerField(default=1)
    items_total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.variation)

    def remove_from_cart(self):
        return "%s?variation_id=%s&quantity=1&delete_cartitem=True" % (reverse("cart"), self.variation.id)


def cartitem_pre_action_receiver(sender, instance, *args, **kwargs):
    qty = instance.quantity
    if qty >= 1:
        price = Decimal(instance.variation.get_price())
        instance.items_total_price = price * qty

pre_save.connect(cartitem_pre_action_receiver, sender=CartItem)


def cartitem_post_action_receiver(sender, instance, *args, **kwargs):
    instance.cart.update_subtotal()


post_save.connect(cartitem_post_action_receiver, sender=CartItem)
post_delete.connect(cartitem_post_action_receiver, sender=CartItem)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    items = models.ManyToManyField(Variation, through=CartItem)
    # timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    # updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    tax_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.23)

    def __str__(self):
        return str(self.id)

    def update_subtotal(self):
        subtotal = 0
        for cartitem in self.cartitem_set.all():
            subtotal += cartitem.items_total_price
        self.subtotal = "{0:.2f}".format(subtotal)
        self.save()


def do_tax_cart_and_pre_receiver(sender, instance, *args, **kwargs):
    subtotal = Decimal(instance.subtotal)
    tax_total = round(subtotal * Decimal(instance.tax_rate), 2)
    instance.tax_total = "{0:.2f}".format(tax_total)
    instance.total_price = "{0:.2f}".format(round(subtotal + tax_total, 2))

pre_save.connect(do_tax_cart_and_pre_receiver, sender=Cart)