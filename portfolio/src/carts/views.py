from django.http import Http404
from django.shortcuts import render
import braintree
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin

from orders.forms import GuestCheckForm
from orders.mixins import CartOrderMixin
from orders.models import UserCheckout
from products.models import Variation
from .models import Cart, CartItem


class CartView(View):
    model = Cart
    template_name = "carts/view.html"

    def get_object(self, *args, **kwargs):
        # set session expiration time as long as browser is open
        self.request.set_expiry(0)
        cart_id = self.request.session.get("cart_id")
        cart = Cart.objects.get_or_create(id=cart_id)[0]
        if cart_id is None:
            self.request.session["cart_id"] = cart.id

        user = self.requst.user
        if user.is_authenticated():
            cart.user = user
            cart.save()
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        item_id = request.GET.get("item")
        delete_item = request.GET.get("delete", False)
        item_added = False
        flash_message = ""

        if item_id:
            item_instance = get_object_or_404(Variation, id=item_id)
            qty = int(request.GET.get("qty", 1))
            try:
                if qty < 1:
                    delete_item = True
            except:
                raise Http404

            cart_position, cart_created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
            if cart_created:
                flash_message = "Item succesfully added to the card."
                item_added = True
            if delete_item:
                flash_message = "Item removed succesfully."
            else:
                if not cart_created:
                    flash_message = "Item has been succesfully updated."
                cart_position.quantity = qty
                cart_position.save()

            if not request.is_ajac():
                return HttpResponseRedirect(reverse("cart"))

        if request.is_ajax():
            try:
                items_total_price = cart_position.items_total_price
            except:
                items_total_price = None

            try:
                subtotal = cart_position.cart.subtotal
            except:
                subtotal = None

            try:
                total_items = cart_position.cart.items.count()
            except:
                total_items = 0

            try:
                tax_total = cart_position.cart.tax_total
            except:
                tax_total = None

            try:
                total_price = cart_item.cart.total_price
            except:
                total_price = None

            data = {
                "deleted": delete_item,
                "flash_message": flash_message,
                "item_added": item_added,
                "items_total_price": items_total_price,
                "subtotal": subtotal,
                "total_items": total_items,
                "tax_total": tax_total,
                "total_price": total_price,
            }
            return  JsonResponse(data)

        context = {"object": cart}
        template = self.template_name
        return render(request, template, context)
    # dodaj cartview w url i podaj link do template:base template:product_detail dodaj przycisk kup