from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View

from products.models import Variation
from .models import Cart, CartItem

# TODO dodaj (nowa funkcja) zlicanie sumy cen produktow tak jak z koszykiem i iloscia jest
# ... jeszcze nie ale bedzie

class ItemCoutView(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():  # jeżeli ajax kolata to mu otworz :D
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


# TODO
# cartview w url i podaj link do template:base template:product_detail
# dodaj przycisk kupda
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
        # TODO cos sie sypie item_id
        item_id = request.GET.get("item_id")
        delete_cart_item = request.GET.get("delete", False)
        cart_item_added = False
        flash_message = ""

        if item_id:
            cart_item_instance = get_object_or_404(Variation, id=item_id)
            qantity = int(request.GET.get("qantity", 1))

            try:
                if qantity < 1:
                    delete_cart_item = True
            except:
                raise Http404

            cart_item, cart_created = CartItem.objects.get_or_create(cart=cart, item=cart_item_instance)

            if cart_created:
                flash_message = "Item succesfully added to the card."
                cart_item_added = True

            if delete_cart_item:
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
            try:
                cart_item_total_price = cart_item.items_total_price
            except:
                cart_item_total_price = None

            try:
                subtotal = cart_item.cart.subtotal
            except:
                subtotal = None

            try:
                total_items = cart_item.cart.items.count()
            except:
                total_items = 0

            try:
                tax_total = cart_item.cart.tax_total
            except:
                tax_total = None

            try:
                total_price = cart_item.cart.total_price
            except:
                total_price = None

            data = {
                "deleted": delete_cart_item,
                "flash_message": flash_message,
                "cart_item_added": cart_item_added,
                "cart_item_total_price": cart_item_total_price,
                "subtotal": subtotal,
                "total_items": total_items,
                "tax_total": tax_total,
                "total_price": total_price,
            }
            return JsonResponse(data)

        context = {"object": cart}
        template = self.template_name
        return render(request, template, context)
