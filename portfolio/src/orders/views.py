from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView
from django.views.generic.edit import CreateView

from orders.forms import UserAddressChooseForm, UserAddressModelForm
from orders.mixins import CartOrderMixin
from orders.models import UserAddress, UserCheckout
from users_profiles.models import UserProfile


# TODO when edit existing address (selecting by choose form) user doesnt edit it
# for real, to not destroy data needed for old orders etc. In fact user add new
# address based on existing data and set it as deafault if needed.
# Old address or deleted change type to outdated
# If added address already exist for user as outdated -> it just change type
# if its other type-> inform it exist.
# Max addreses on list is 10, before adding new you have to delete any other.

class AddressSelectFormView(CartOrderMixin, FormView):
    # TODO add phone (from profile data, but editable) info for curier etc.
    form_class = UserAddressChooseForm
    template_name = "orders/address.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_cart() is None:
            messages.success(self.request, "In a moment you'll be redirected to product list.")
            return redirect("cart")
        billing_address, shipping_address = self.get_addresses()
        if billing_address.count() == 0 and shipping_address.count() == 0:
            messages.success(self.request, "Please add your address before continuing.")
            return redirect("add_address")
        elif billing_address.count() == 0 or shipping_address.count() == 0:
            messages.success(self.request, "Please add your address before continuing."
                                           "\nOr use the same for shipping.")

        return super(AddressSelectFormView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        # TODO add "use_the_same_address" checkbox for each field if "parent" exist
        form = super(AddressSelectFormView, self).get_form()
        billing_address, shipping_address = self.get_addresses()
        form.fields["billing_address"].queryset = billing_address
        form.fields["shipping_address"].queryset = shipping_address
        return form

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(AddressSelectFormView, self).get_form_kwargs()
        user = self.request.user
        if user.is_authenticated:  # get default addreses to set in form_class
            user_profile = UserProfile.objects.get(user=user)
            default_billing_address = user_profile.default_billing_address
            default_shipping_address = user_profile.default_shipping_address
            if default_billing_address is not None:
                form_kwargs["default_billing_address_id"] = default_billing_address.id
            if default_shipping_address is not None:
                form_kwargs["default_shipping_address_id"] = default_shipping_address.id
        return form_kwargs

    def get_addresses(self):
        if self.request.user.is_authenticated():
            email = self.request.user.email
            billing_address = UserAddress.objects.filter(user_checkout__email=email, type='billing')
            shipping_address = UserAddress.objects.filter(user_checkout__email=email, type='shipping')
        else:  # anon user
            billing_address_ids = self.request.session.get("billing_address_ids", [])
            shipping_address_ids = self.request.session.get("shipping_address_ids", [])
            if billing_address_ids or shipping_address_ids:
                billing_address = UserAddress.objects.filter(id__in=billing_address_ids, type='billing')
                shipping_address = UserAddress.objects.filter(id__in=shipping_address_ids, type='shipping')
            else:  # no ids in session- return empty queries
                billing_address, shipping_address = UserAddress.objects.none(), UserAddress.objects.none()
        return billing_address, shipping_address

    def form_valid(self, form):
        self.set_chosen_addresses_ids_in_session(form)
        # TODO Set address the same for each of label -> create if not exist
        # add checkboxes for logged in users to set default shwiching addresses.
        # Add jq stuff too.
        # Exclude outdated addresses from add_form
        return super(AddressSelectFormView, self).form_valid(form)

    def set_chosen_addresses_ids_in_session(self, form):
        session_data = self.request.session
        session_data["billing_address_id"] = form.cleaned_data["billing_address"].id
        session_data["shipping_address_id"] = form.cleaned_data["shipping_address"].id

    def get_success_url(self):
        return reverse("checkout")


class UserAddressCreateView(CreateView):
    # TODO add "use_the_same_address" checkbox for each field if "parent" exist
    # add set as default for billing or shipping address
    model = UserAddress
    form_class = UserAddressModelForm
    template_name = "products/product_form.html"

    def get_form(self, *args, **kwargs):
        return super(UserAddressCreateView, self).get_form(*args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(UserAddressCreateView, self).get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs["user_is_auth"] = True
        return kwargs

    def form_valid(self, form):
        self.get_user_checkout()
        form.instance.user_checkout = self.get_user_checkout()

        # TODO when addres already exist : for user -> use existing, inform that exist
        #                                  for guest -> (check by session id, use existing, dont inform

        # Save new addres as default (in profile) if user want to or add it to session for guest
        self.object = form.save()
        new_address = self.object
        user = self.request.user
        # TODO exclude outdated type in form
        address_type = form.cleaned_data["type"]
        if user.is_authenticated:
            set_address_as_default = form.cleaned_data["set_address_as_default"]
            if set_address_as_default:
                user_profile = UserProfile.objects.get(user=user)
                if address_type == 'billing':
                    user_profile.default_billing_address = new_address
                elif address_type == 'shipping':
                    user_profile.default_shipping_address = new_address
                user_profile.save()
        else:  # for guests
            session = self.request.session
            if address_type == 'billing':
                session.setdefault('billing_address_ids', []).append(new_address.id)
            elif address_type == 'shipping':
                session.setdefault('shipping_address_ids', []).append(new_address.id)
            session.save()
        return super(UserAddressCreateView, self).form_valid(form)

    def get_user_checkout(self):
        user_checkout_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        return user_checkout

    def get_success_url(self):
        return reverse("checkout")