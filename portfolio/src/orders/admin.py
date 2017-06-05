from django.contrib import admin
from .models import Order, UserAddress, UserCheckout


admin.site.register(Order)
admin.site.register(UserAddress)
admin.site.register(UserCheckout)
