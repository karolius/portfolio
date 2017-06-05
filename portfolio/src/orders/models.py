from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from carts.models import Cart


ORDER_STATUS_CHOICES = (("canceled", "Canceled"),
                        ("created", "Created"),
                        ('paid', 'Paid'),
                        ('shipped', 'Shipped'),)


ADDRESS_TYPE = (('billing', 'Billing'),
                ('shipping', 'Shipping'),
                )


class UserCheckout(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, blank=True, null=True)
    email = models.EmailField(blank=False, null=False, max_length=120)
    # payment checkout

    def __str__(self):
        return self.email


class UserAddress(models.Model):
    user_checkout = models.ForeignKey("UserCheckout")
    type = models.CharField(max_length=120, choices=ADDRESS_TYPE)
    street = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    zipcode = models.CharField(max_length=120)

    def __str__(self):
        user = self.user_checkout.user
        email = self.user_checkout.email
        return "%s-%s" % (user if user else email, self.street)


class Order(models.Model):
    user = models.ForeignKey("UserCheckout")  # it have to bee null=True
    cart = models.ForeignKey(Cart)
    status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default="created")
    billing_address = models.ForeignKey("UserAddress", related_name="billing_address")
    shipping_address = models.ForeignKey("UserAddress", related_name="shipping_address")
    shipping_cost = models.DecimalField(decimal_places=2, max_digits=30, default="12.00")
    order_total = models.DecimalField(decimal_places=2, max_digits=30, default="0.00")

    def __str__(self):
        return str(self.id)