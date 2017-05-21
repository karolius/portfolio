from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete

from products.models import Variation, Product


class CartPosition(models.Model):
    cart = models.ForeignKey("Cart")
    item = models.ForeignKey(Variation)
    quantity = models.IntegerField(default=1)
    items_total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.item)


def cart_position_pre_action_receiver(sender, instance, *args, **kwargs):
    qty = instance.quantity
    if qty >= 1:
        price = Decimal(instance.item.get_price())
        instance.items_total_price = price * qty

pre_save.connect(cart_position_pre_action_receiver, sender=CartPosition)


def cart_position_post_action_receiver(sender, instance, *args, **kwargs):
    instance.cart.update_subtotal()


post_save.connect(cart_position_post_action_receiver, sender=CartPosition)
post_delete.connect(cart_position_post_action_receiver, sender=CartPosition)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    items = models.ManyToManyField(Variation, through=CartPosition)
    # timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    # updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    tax_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.id)

    def update_subtotal(self):
        subtotal = 0
        for cart_position in self.cartposition_set.all():
            subtotal += cart_position.items_total_price
        self.subtotal = "{0:.2f}".format(subtotal)
        self.save()


def do_tax_cart_and_pre_receiver(sender, instance, *args, **kwargs):
    subtotal = Decimal(instance.subtotal)
    tax_total = round(subtotal * Decimal(instance.tax_rate), 2)
    instance.tax_total = "{0:.2f}".format(tax_total)
    instance.total_price = "{0:.2f}".format(round(subtotal + tax_total, 2))

pre_save.connect(do_tax_cart_and_pre_receiver, sender=Cart)