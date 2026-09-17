import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from cart.cart import Cart
from accounts.models import Address
from .models import Order, OrderItem, Coupon
from .paystack import initialize_payment, verify_payment


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('cart_detail')

    addresses = request.user.addresses.all()
    subtotal = cart.get_total()
    discount = Decimal('0')
    coupon = None

    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
            if coupon.is_valid():
                discount = subtotal * (Decimal(coupon.discount_percent) / Decimal('100'))
        except Coupon.DoesNotExist:
            coupon = None

    total = subtotal - discount

    if request.method == 'POST':
        address_id = request.POST.get('address')
        address = get_object_or_404(Address, id=address_id, user=request.user)

        order = Order.objects.create(
            customer=request.user,
            full_name=address.full_name,
            phone_number=address.phone_number,
            address_line=address.address_line,
            city=address.city,
            state=address.state,
            coupon=coupon,
            subtotal=subtotal,
            discount=discount,
            total=total,
            payment_reference=str(uuid.uuid4()),
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                variant=item['variant'],
                quantity=item['quantity'],
                unit_price=item['price'],
                subtotal=item['subtotal'],
            )

        callback_url = request.build_absolute_uri(reverse('verify_order_payment'))
        response = initialize_payment(
            email=request.user.email,
            amount_naira=order.total,
            reference=order.payment_reference,
            callback_url=callback_url,
        )

        if response.get('status'):
            authorization_url = response['data']['authorization_url']
            return redirect(authorization_url)
        else:
            order.delete()
            messages.error(request, "Could not start payment. Please try again.")
            return redirect('checkout')

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'addresses': addresses,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'coupon': coupon,
    })


@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if code:
            try:
                coupon = Coupon.objects.get(code__iexact=code)
                if coupon.is_valid():
                    request.session['coupon_code'] = coupon.code
                    messages.success(request, f"Coupon '{coupon.code}' applied — {coupon.discount_percent}% off.")
                else:
                    messages.error(request, "This coupon is invalid or expired.")
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid coupon code.")
    return redirect('checkout')


@login_required
def verify_order_payment_view(request):
    reference = request.GET.get('reference')
    if not reference:
        messages.error(request, "No payment reference provided.")
        return redirect('my_orders')

    order = get_object_or_404(Order, payment_reference=reference, customer=request.user)
    result = verify_payment(reference)

    if result.get('status') and result['data']['status'] == 'success':
        paid_amount_naira = result['data']['amount'] / 100
        if paid_amount_naira == float(order.total):
            order.payment_status = 'paid'
            order.status = 'payment_confirmed'
            order.save()
            cart = Cart(request)
            cart.clear()
            request.session.pop('coupon_code', None)
            messages.success(request, "Payment confirmed! Your order has been placed.")
        else:
            order.payment_status = 'failed'
            order.save()
            messages.error(request, "Payment amount mismatch. Please contact support.")
    else:
        order.payment_status = 'failed'
        order.save()
        messages.error(request, "Payment was not successful.")

    return redirect('order_detail', order_id=order.id)


@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user)
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})