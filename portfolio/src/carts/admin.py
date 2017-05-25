from django.contrib import admin
from .models import (CartItem,
                     Cart)


class CartItemInLine(admin.TabularInline):
    model = CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "total_price"]
    list_display_links = ["__str__", "user"]
    list_filter = ["user"]
    search_fields = ["user"]
    inlines = [CartItemInLine]

    class Meta:
        model = Cart


admin.site.register(Cart, CartAdmin)