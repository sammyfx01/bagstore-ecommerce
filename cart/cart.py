from products.models import Product, ProductVariant

CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def _get_key(self, product_id, variant_id=None):
        return f"{product_id}_{variant_id}" if variant_id else str(product_id)

    def add(self, product, quantity=1, variant=None):
        key = self._get_key(product.id, variant.id if variant else None)
        if key not in self.cart:
            self.cart[key] = {
                'product_id': product.id,
                'variant_id': variant.id if variant else None,
                'quantity': 0,
            }
        self.cart[key]['quantity'] += quantity
        self.save()

    def update(self, key, quantity):
        if key in self.cart:
            if quantity > 0:
                self.cart[key]['quantity'] = quantity
            else:
                self.remove(key)
            self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        for key, item in self.cart.items():
            product = Product.objects.get(pk=item['product_id'])
            variant = None
            if item['variant_id']:
                variant = ProductVariant.objects.get(pk=item['variant_id'])
            price = variant.price if variant else product.price
            yield {
                'key': key,
                'product': product,
                'variant': variant,
                'quantity': item['quantity'],
                'price': price,
                'subtotal': price * item['quantity'],
            }

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total(self):
        return sum(item['subtotal'] for item in self)