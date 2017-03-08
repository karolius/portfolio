from django.contrib import admin
from .models import (Product,
                     Thumbnail,
                     Variation,
                     Category)


class ThumbnailInLine(admin.TabularInline):
    extra = 1
    model = Thumbnail


class ProductAdmin(admin.ModelAdmin):
    list_display = ["__str__", "price", "sale_price", "status"]
    list_display_links = ["__str__"]
    list_editable = ["sale_price"]
    list_filter = ["price"]
    search_fields = ["title", "description"]
    inlines = [ThumbnailInLine]

    class Meta:
        model = Product


class VariationAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "__str__", "price", "sale_price"]
    list_display_links = ["__str__"]
    list_editable = ["sale_price"]
    list_filter = ["price"]
    search_fields = ["title", "description", "product"]

    class Meta:
        model = Variation

admin.site.register(Product, ProductAdmin)
admin.site.register(Thumbnail)
admin.site.register(Variation, VariationAdmin)
admin.site.register(Category)