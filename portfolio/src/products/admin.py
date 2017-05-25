from django.contrib import admin
from django.utils.text import slugify

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
# admin.site.register(Category)


from django.contrib import messages


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')

    def save_model(self, request, obj, form, change):
        # Adds flash message that slug based on title already exists, so system create a randomg generated one.
        slug_by_title = slugify(obj.title)
        slug_by_title_exists = type(obj).objects.filter(slug=slug_by_title).exists()
        if not obj.slug and slug_by_title_exists:
            messages.add_message(request, messages.INFO,
                                 'Slug isn\'t the same as it would have been created by category '
                                 'title, it means slug with this name already existed.')
        super(CategoryAdmin, self).save_model(request, obj, form, change)