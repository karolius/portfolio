from django import forms
from django.forms.models import modelformset_factory

from .models import Product, Category, Variation


class ProductModelForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'title',
            'description',
            'price',
            'sale_price',
            'sale_active',
            'category',
            'media',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': 'Title'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Description of the product'
                }
            ),
            'category': forms.CheckboxSelectMultiple()
        }

    def clean(self, **kwargs):
        cleaned_data = super(ProductModelForm, self).clean(**kwargs)
        return cleaned_data

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if len(title) < 4:
            raise forms.ValidationError(
                "Title must be greater than 3 characters long")
        return title

    def clean_sale_active(self):
        sale_active = self.cleaned_data.get("sale_active")
        if sale_active:
            sale_price = self.cleaned_data.get("sale_price")
            if not sale_price:
                raise forms.ValidationError(
                    "You selected SALE without setting sale price, please correct it.")
        return sale_active

    def check_range(self, var, min=0.03, max=15000.01):
        if min <= var < max:
            return True
        return False

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price:
            if not self.check_range(var=price):
                raise forms.ValidationError(
                    "Price must be greater than $0.03 and less than $15 000")
        return price

    def clean_sale_price(self):
        price = self.cleaned_data.get("price")
        sale_price = self.cleaned_data.get("sale_price")
        if sale_price:
            if not self.check_range(var=sale_price, max=price):
                raise forms.ValidationError(
                    "Sale price must be greater than $0.03 and less than normal price")
        return sale_price

    def clean_media(self):
        media = self.cleaned_data.get("media")
        if media:
            return media
        return None

    def clean_category(self):
        category = self.cleaned_data.get("category")
        if category.count() == 0:
            default_category = Category.objects.get(title="Other")
            category = [default_category]
        return category


class VariationInventoryForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = [
            'title',
            'sub_description',
            'price',
            'sale_price',
            'sale_active',
        ]


VariationInventoryFormSet = modelformset_factory(Variation,
                                                 form=VariationInventoryForm,
                                                 extra=2)