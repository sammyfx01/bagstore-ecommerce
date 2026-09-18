from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product
from reviews.forms import ReviewForm


def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    categories = Category.objects.filter(is_active=True)
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    sort = request.GET.get('sort')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'query': query or '',
        'sort': sort or '',
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]
    reviews = product.reviews.filter(is_approved=True)
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = reviews.filter(customer=request.user).exists()
    review_form = ReviewForm()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'user_has_reviewed': user_has_reviewed,
    })
def about(request):
    return render(request, 'about.html')