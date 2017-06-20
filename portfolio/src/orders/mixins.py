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

    def add_session_address_ids(self, address):
        session = self.request.session
        if address.type == 'billing':
            session.setdefault('billing_address_ids', []).append(address.id)
        elif address.type == 'shipping':
            session.setdefault('shipping_address_ids', []).append(address.id)
        session.save()