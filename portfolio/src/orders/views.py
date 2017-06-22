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

# Changing email in choseform or add form with flag to redirect just once.
# Add button on detail page to checkout, show in right upper corner u_name/guest email
# Allow guest/user to drop session data or some parts of it

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
        # TODO work on error messages in clean_*
        # what happens when default addres becomes outdated (-> change it to inactive billing/shipping)
        # refactor code
        form = super(AddressSelectFormView, self).get_form()

        # Fill queryset with proper email data, any used for users + default and session data for guests.
        billing_address_field = form.fields["billing_address"]
        shipping_address_field = form.fields["shipping_address"]
        billing_address, shipping_address = self.get_addresses()
        if self.request.user.is_authenticated:
            # For auth users use their default addreses as empty_labels in choice fields
            # and exclude them from
            default_billing_address, default_shipping_address = self.get_default_addresses()
            if default_billing_address:
                # billing_address = billing_address.exclude(id=default_billing_address.id)
                billing_address_field.empty_label = billing_address.filter(id=default_billing_address.id)
            if default_shipping_address:
                # shipping_address = shipping_address.exclude(id=default_shipping_address.id)
                shipping_address_field.empty_label = shipping_address.filter(id=default_shipping_address.id)
        billing_address_field.queryset = billing_address
        shipping_address_field.queryset = shipping_address
        return form

    # def get_form_kwargs(self, *args, **kwargs):
    #     form_kwargs = super(AddressSelectFormView, self).get_form_kwargs()
    #     if self.request.user.is_authenticated:  # get default addreses to set in form_class
    #         self.set_default_addresses_in_kwargs(form_kwargs)
    #     return form_kwargs

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
        use_the_same_for_shipping = form.cleaned_data["use_the_same_for_shipping"]
        if use_the_same_for_shipping:
            # Create or get address
            billing_address = form.cleaned_data["billing_address"]
            shipping_address = form.cleaned_data["shipping_address"]
            if billing_address:
                new_address = self.user_address_get_or_create_by(base_instance=billing_address)
                form.cleaned_data["shipping_address"] = new_address
            elif shipping_address:
                new_address = self.user_address_get_or_create_by(base_instance=shipping_address)
                form.cleaned_data["billing_address"] = new_address
            else:
                new_address = None
            if not self.request.user.is_authenticated and new_address is not None:
                # TODO be sure new addres exist, and check what happens when address change to outdated and new is
                # populated by it.
                # TODO change form that it explicitly tell what user can do (eg. theres billing and shipping what happes when mark use the same)
                self.add_address_ids_to_session(address=new_address)

        self.set_chosen_addresses_ids_in_session(form)
        # TODO Set address the same for each of label -> create if not exist
        # add checkboxes for logged in users to set default shwiching addresses.
        # Add jq stuff too.
        # Exclude outdated addresses from add_form
        return super(AddressSelectFormView, self).form_valid(form)

    def user_address_get_or_create_by(self, base_instance):
        if base_instance.type == 'shipping':
            type = 'billing'
        else:
            type = 'shipping'
        return UserAddress.objects.get_or_create(
            user_checkout=base_instance.user_checkout,
            type=type,
            street=base_instance.street,
            city=base_instance.city,
            state=base_instance.state,
            zipcode=base_instance.zipcode,
        )[0]

    def set_chosen_addresses_ids_in_session(self, form):
        session_data = self.request.session
        session_data["billing_address_id"] = form.cleaned_data["billing_address"].id
        session_data["shipping_address_id"] = form.cleaned_data["shipping_address"].id
        session_data.save()

    def get_success_url(self):
        return reverse("checkout")

    def get_default_addresses(self):
        user_profile = UserProfile.objects.get(user=self.request.user)
        default_billing_address = user_profile.default_billing_address
        default_shipping_address = user_profile.default_shipping_address
        return default_billing_address, default_shipping_address


class UserAddressCreateView(CartOrderMixin, CreateView):
    # TODO add "use_the_same_for_shipping" checkbox for each field if "parent" exist
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

        self.object = form.save()
        new_address = self.object
        # TODO exclude outdated type in form
        set_address_as_default = form.cleaned_data.get("set_address_as_default", False)
        if self.request.user.is_authenticated and set_address_as_default:
            self.set_user_profile_default_address(new_address)
        else:  # for guests
            self.add_address_ids_to_session(address=new_address)
        return super(UserAddressCreateView, self).form_valid(form)

    def get_user_checkout(self):
        user_checkout_id = self.request.session.get("user_checkout_id")
        user_checkout = UserCheckout.objects.get(id=user_checkout_id)
        return user_checkout

    def get_success_url(self):
        return reverse("checkout")

    def set_user_profile_default_address(self, new_address):
        user_profile = UserProfile.objects.get(user=self.request.user)
        if new_address.type == 'billing':
            user_profile.default_billing_address = new_address
        elif new_address.type == 'shipping':
            user_profile.default_shipping_address = new_address
        user_profile.save()

