from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .forms import ReviewForm
from .models import Review


@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if Review.objects.filter(product=product, customer=request.user).exists():
        messages.error(request, "You've already reviewed this product.")
        return redirect('product_detail', slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.customer = request.user
            review.save()
            messages.success(request, "Thank you! Your review has been submitted.")
            return redirect('product_detail', slug=product.slug)
        else:
            messages.error(request, "Please provide a valid rating.")

    return redirect('product_detail', slug=product.slug)