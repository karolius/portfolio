from django.contrib import admin
from .models import (Product,
                     Thumbnail,)


class ThumbnailInLine(admin.TabularInline):
    extra = 1
    model = Thumbnail


class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "__str__", "price", "sale_price"]
    list_display_links = ["__str__"]
    list_editable = ["sale_price"]
    list_filter = ["price"]
    search_fields = ["title", "description"]
    inlines = [ThumbnailInLine]

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
admin.site.register(Thumbnail)