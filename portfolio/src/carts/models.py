from django.db import models
from django.conf import settings



from products.models import Product, Variation


class CartPosition(models.Model):
    cart = models.ForeignKey("Cart")
    item = models.ForeignKey(Variation)
    quantity = models.IntegerField(default=1)
    items_total_price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.item.title


def cart_position_pre_action_receiver(sender, instance, *args, **kwargs):
    qty = instance.quantity
    if qty >= 1:
        price = Decimal(instance.item.get_price())
        instance.line_item_total = price * qty

pre_save.onnect(cart_position_pre_action_receiver, sender=CartPosition)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    items = models.ManyToManyField(Variation, through=CartPosition)
    # timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    # updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    total_price = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return self.id
