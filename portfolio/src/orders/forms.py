from django import forms
from django.forms import ModelForm

from orders.models import UserCheckout, UserAddress


class GuestCheckoutForm(forms.Form):
    email1 = forms.EmailField(label="Email Address")
    email2 = forms.EmailField(label="Verify Email")

    def clean_email2(self):
        email1 = self.cleaned_data.get("email1")
        email2 = self.cleaned_data.get("email2")
        user_checkout = UserCheckout.objects.filter(email=email1).first()
        if email1 != email2:
            raise forms.ValidationError(
                "Emails aren't the same, please correct it.")
        elif user_checkout is not None:
            if user_checkout.user is not None:
                raise forms.ValidationError(
                    "Account with this email already exists, please login, or try other email.")
        return email2


class UserAddressChooseForm(forms.Form):
    field_order = None

    def __init__(self, *args, **kwargs):
        default_billing_address_id = kwargs.pop("default_billing_address_id", None)
        default_shipping_address_id = kwargs.pop("default_shipping_address_id", None)
        super(UserAddressChooseForm, self).__init__(*args, **kwargs)

        self.fields['use_the_same_for_shipping_as_billing_address'] = forms.BooleanField()
        self.fields['use_the_same_for_billing_as_shipping_address'] = forms.BooleanField()
        self.set_empty_address_label(field_name='billing_address', address_id=default_billing_address_id)
        self.set_empty_address_label(field_name='shipping_address', address_id=default_shipping_address_id)

    def set_empty_address_label(self, field_name, address_id):
        if address_id is not None:
            billing_address = UserAddress.objects.get(id=address_id)
            self.fields[field_name].empty_label = billing_address

    billing_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(type="billing"),
        empty_label=None)
    shipping_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(type="shipping"),
        empty_label=None)


class UserAddressModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_is_auth = kwargs.pop('user_is_auth', None)
        super().__init__(*args, **kwargs)
        if user_is_auth:
            self.fields['set_address_as_default'] = forms.BooleanField()

    class Meta:
        model = UserAddress
        fields = [
            'type',
            'street',
            'city',
            'state',
            'zipcode',
        ]