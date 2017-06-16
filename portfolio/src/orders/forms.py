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
    billing_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(type="billing"),
        empty_label=None)
    shipping_address = forms.ModelChoiceField(
        queryset=UserAddress.objects.filter(type="shipping"),
        empty_label=None)


class UserAddressModelForm(forms.ModelForm):
    # TODO add set as default field (when uncheck set Null on user_profile)
    # if
    # set_as_default = forms.BooleanField()
    #
    # def __init__(self):
    #     super().__init__()
    #     if check_something():
    #         self.fields['receive_newsletter'].initial = True

    class Meta:
        model = UserAddress
        fields = [
            'type',
            'street',
            'city',
            'state',
            'zipcode',
        ]