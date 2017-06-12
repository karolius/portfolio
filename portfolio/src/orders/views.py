from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import FormView

from orders.forms import UserAddressForm
from orders.models import UserAddress, Order


class AddressSelectFormView(FormView):
    form_class = UserAddressForm
    template_name = "orders/address.html"

    def get_form(self, form_class=None):
        form = super(AddressSelectFormView, self).get_form()
        self.set_form_addreses_according_to_auth(form)
        return form

    def set_form_addreses_according_to_auth(self, form):
        if self.request.user.is_authenticated():
            email = self.request.user.email
            form.fields["billing_address"].queryset = UserAddress.objects.filter(user_checkout__email=email)
            form.fields["shipping_address"].queryset = UserAddress.objects.filter(user_checkout__email=email)
        else:
            billing_address_id = self.request.session.get("billing_address_id", [])
            shipping_address_id = self.request.session.get("shipping_address_id", [])
            form.fields["billing_address"].queryset = UserAddress.objects.filter(id__in=billing_address_id)
            form.fields["shipping_address"].queryset = UserAddress.objects.filter(id__in=shipping_address_id)

    def form_valid(self, form):
        self.set_addresses_ids_in_session(form)
        return super(AddressSelectFormView, self).form_valid(form)

    def set_addresses_ids_in_session(self, form):
        session_data = self.request.session
        session_data["billing_address_id"] = form.cleaned_data["billing_address"].id
        session_data["shipping_address_id"] = form.cleaned_data["shipping_address"].id

    def get_success_url(self):
        return reverse("checkout")