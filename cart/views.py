from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product, ProductVariant
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))

    variant = None
    variant_id = request.POST.get('variant')
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    cart.add(product=product, quantity=quantity, variant=variant)
    messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart_detail')


def cart_update(request, key):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(key, quantity)
    return redirect('cart_detail')


def cart_remove(request, key):
    cart = Cart(request)
    cart.remove(key)
    messages.success(request, "Item removed from your cart.")
    return redirect('cart_detail')