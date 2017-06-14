from carts.models import Cart


class CartOrderMixin(object):
    def __init__(self):
        self.request = None

    def get_cart(self):
        cart_id = self.request.session.get("cart_id")
        if cart_id is None:
            return None
        cart = Cart.objects.get(id=cart_id)
        if cart.items.count() < 1:
            return None
        return cart