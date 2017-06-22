from django import forms

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
    field_order = ['billing_address', 'shipping_address', 'use_the_same_for_shipping', 'use_the_same_for_billing']
    use_the_same_for_shipping = forms.BooleanField(required=False)
    use_the_same_for_billing = forms.BooleanField(required=False)
    billing_address = forms.ModelChoiceField(queryset=None, required=False, empty_label=None)
    shipping_address = forms.ModelChoiceField(queryset=None, required=False, empty_label=None)

    def clean_shipping_address(self):
        billing_address = self.cleaned_data.get("billing_address")
        shipping_address = self.cleaned_data.get("shipping_address")
        if not billing_address and not shipping_address:
            raise forms.ValidationError("You need to chose billing or shipping address at last.")
        return shipping_address
    #
    # def clean_use_the_same_for_shipping(self):
    #     use_the_same_for_shipping = self.cleaned_data.get("use_the_same_for_shipping")
    #     if use_the_same_for_shipping:
    #         billing_address = self.cleaned_data.get("billing_address")
    #         if not billing_address:
    #             raise forms.ValidationError("You need to chose billing address to use the same for shipping.")
    #     return use_the_same_for_shipping

    def clean_use_the_same_for_billing(self):
        # The same fields matched- conflict.
        use_the_same_for_shipping = self.cleaned_data.get("use_the_same_for_shipping")
        use_the_same_for_billing = self.cleaned_data.get("use_the_same_for_billing")
        if use_the_same_for_shipping and use_the_same_for_billing:
            raise forms.ValidationError("You can't match both option. Choose explicitly what have to be done.")

        billing_address = self.cleaned_data.get("billing_address")
        shipping_address = self.cleaned_data.get("shipping_address")
        if not use_the_same_for_billing:
            if not use_the_same_for_shipping:
                if not shipping_address:
                    raise forms.ValidationError(
                        "You need to chose shipping address or match to use the same as billing.")
            else:
                if not billing_address:
                    raise forms.ValidationError(
                        "You need to chose billing address or match to use the same as shipping.")
        else:
            if not shipping_address:
                raise forms.ValidationError("First you need to chose shipping address to use the same for billing.")
        return use_the_same_for_shipping


class UserAddressModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_is_auth = kwargs.pop('user_is_auth', None)
        super().__init__(*args, **kwargs)
        if user_is_auth:
            self.fields['set_address_as_default'] = forms.BooleanField(required=False)
        self.fields['type'].choices = [(x1, x2) for x1, x2 in self.fields['type'].choices
                                       if x1 != 'outdated']

    class Meta:
        model = UserAddress
        fields = [
            'type',
            'street',
            'city',
            'state',
            'zipcode',
        ]