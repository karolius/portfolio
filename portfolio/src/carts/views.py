from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin

from orders.forms import GuestCheckoutForm
from orders.models import UserCheckout, Order, UserAddress
from products.models import Variation
from .models import Cart, CartItem


class ItemCoutView(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            cart_item_count = 0
            cart_sum_price = 0
            cart_id = self.request.session.get("cart_id")
            if cart_id is not None:
                cart = Cart.objects.get(id=cart_id)
                cart_item_count = cart.items.count()
                cart_sum_price = str(cart.total_price)

            # set count, then it wont flip
            request.session["cart_item_count"] = cart_item_count
            request.session["cart_sum_price"] = cart_sum_price
            return JsonResponse({"cart_item_count": cart_item_count,
                                 "cart_sum_price": cart_sum_price})
        return Http404


class CartView(View):
    model = Cart
    template_name = "carts/view.html"

    def get_object(self, *args, **kwargs):
        # set session expiration time as long as browser is open
        self.request.session.set_expiry(0)
        cart_id = self.request.session.get("cart_id")
        cart, cart_created = Cart.objects.get_or_create(id=cart_id)
        if cart_created:
            self.request.session["cart_id"] = cart.id

        user = self.request.user
        if user.is_authenticated():
            cart.user = user
            cart.save()
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        variation_id = request.GET.get("variation_id")
        delete_cartitem = request.GET.get("delete_cartitem", False)
        cart_item_added = False
        flash_message = ""

        if variation_id:
            qantity = int(request.GET.get("qantity", 1))
            delete_cartitem = self.check_qty_or_raise404(delete_cartitem, qantity)

            variation = get_object_or_404(Variation, id=variation_id)
            cart_item, cart_created = CartItem.objects.get_or_create(cart=cart, variation=variation)
            if cart_created:
                flash_message = "Item succesfully added to the card."
                cart_item_added = True

            if delete_cartitem:
                flash_message = "Item removed succesfully."
                cart_item.delete()
            else:
                if not cart_created:
                    flash_message = "Item has been succesfully updated."
                cart_item.quantity = qantity
                cart_item.save()

            if not request.is_ajax():
                return HttpResponseRedirect(reverse("cart"))

        if request.is_ajax():
            data = {
                "deleted": delete_cartitem,
                "flash_message": flash_message,
                "cart_item_added": cart_item_added,
                "cart_item_total_price": self.get_cart_item_total_price_or_none(cart_item),
                "subtotal": self.get_subtotal_or_none(cart_item),
                "total_items": self.get_total_items(cart_item),
                "tax_total": self.get_tax_total_or_none(cart_item),
                "total_price": self.get_total_price_or_none(cart_item),
            }
            return JsonResponse(data)

        context = {"object": cart}
        template = self.template_name
        return render(request, template, context)

    def check_qty_or_raise404(self, delete_cartitem, qantity):
        try:
            if qantity < 1:
                delete_cartitem = True
        except:
            raise Http404
        return delete_cartitem

    def get_total_price_or_none(self, cart_item):
        try:
            total_price = cart_item.cart.total_price
        except:
            total_price = None
        return total_price

    def get_tax_total_or_none(self, cart_item):
        try:
            tax_total = cart_item.cart.tax_total
        except:
            tax_total = None
        return tax_total

    def get_total_items(self, cart_item):
        try:
            total_items = cart_item.cart.items.count()
        except:
            total_items = 0
        return total_items

    def get_subtotal_or_none(self, cart_item):
        try:
            subtotal = cart_item.cart.subtotal
        except:
            subtotal = None
        return subtotal

    def get_cart_item_total_price_or_none(self, cart_item):
        try:
            cart_item_total_price = cart_item.items_total_price
        except:
            cart_item_total_price = None
        return cart_item_total_price


# class CheckoutView(DetailView):
#     model = Cart
#     # template_name = "carts/checkout_view.html"
#
#     def get_context_data(self, **kwargs):
#         context = super(CheckoutView, self).get_context_data()
#         user = self.request.user
#         user_is_auth = user.is_authenticated()
#         order = self.get_order()
#
#
#
#
#         return context
#
#     def get_cart(self):
#         cart_id = self.request.session.get("cart_id")
#         if cart_id is None:
#             return None
#         cart = Cart.objects.get(id=cart_id)
#         if cart.items.count < 1:
#             return None
#         return cart
#
#     def get_order(self):
#         cart = self.get_cart()
#         if cart is None:
#             return None
#
#         order_id = self.request.session.get("order_id")
#         if order_id is None:
#             order = Order.objects.create(cart=cart)
#             self.request.session["order_id"] = order.id
#         else:
#             order = Order.objects.get(id=order_id)
#         return order


class CheckoutView(FormMixin, DetailView):
    model = Cart
    template_name = "carts/checkout.html"
    form_class = GuestCheckoutForm

    def get_object(self, queryset=None):
        cart_id = self.request.session.get("cart_id")
        if cart_id is None:
            return None
        return Cart.objects.get(id=cart_id)

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data()
        user = self.request.user
        user_is_auth = False

        if user.is_authenticated:
            # always overwrite previous session data
            user_checkout = UserCheckout.objects.get_or_create(email=user.email)[0]
            self.request.session["user_checkout_id"] = user_checkout.id

        user_checkout_id = self.request.session.get("user_checkout_id")
        if user_checkout_id is not None:
            user_is_auth = True
        else:
            context["email_form"] = self.get_form()
            context["login_form"] = AuthenticationForm()
            context["next_url"] = self.request.build_absolute_uri()

        context["user_is_auth"] = user_is_auth
        return context

    def get_success_url(self):
        return reverse("checkout")

    def post(self, request):
        self.object = self.get_object()

        user = self.request.GET.user
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get("email1")
            user_checkout, user_checkout_created = UserCheckout.objects.get_or_create(email=email)
            if user_checkout_created:
                self.request.session["user_checkout_id"] = user_checkout.id
            return self.form_valid(form)
        elif user.is_authenticated:
            email = user.email
            user_checkout, user_checkout_created = UserCheckout.objects.get_or_create(email=email)
            if user_checkout_created:
                self.request.session["user_checkout_id"] = user_checkout.id
        return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        get_data = super(CheckoutView, self).get(request, *args, **kwargs)
        session_data = self.request.session
        user_checkout_id = session_data.get("user_checkout_id")
        if user_checkout_id:
            cart = self.get_object()
            if cart is None:
                return redirect("cart")

            order_id = session_data.get("order_id")
            if order_id:
                order = Order.objects.get(id=order_id)
            else:
                order = Order()
                session_data["order_id"] = order.id  # Order.objects.create

            billing_address_id = session_data.get("billing_address_id")
            shipping_address_id = session_data.get("shipping_address_id")
            if billing_address_id is None or shipping_address_id is None:
                return redirect("order_address")

            order.cart = cart
            order.user_checkout = UserCheckout.objects.get(id=user_checkout_id)
            order.billing_address = UserAddress.objects.get(id=billing_address_id)
            order.shipping_address = UserAddress.objects.get(id=shipping_address_id)
            order.save()

            # status = models.
            # shipping_cost
            # order_total

        return get_data