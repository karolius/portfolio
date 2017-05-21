from django.contrib import admin
from .models import (CartPosition,
                     Cart)


class CartPositionInLine(admin.TabularInline):
    model = CartPosition


class CartAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "total_price"]
    list_display_links = ["__str__", "user"]
    list_filter = ["user"]
    search_fields = ["user"]
    inlines = [CartPositionInLine]

    class Meta:
        model = Cart


admin.site.register(Cart, CartAdmin)