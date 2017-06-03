from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View

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
        cart = Cart.objects.get_or_create(id=cart_id)[0]
        if cart_id is None:
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
