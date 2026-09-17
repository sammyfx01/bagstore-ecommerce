from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


@staff_member_required
def dashboard(request):
    paid_orders = Order.objects.filter(payment_status='paid')

    total_revenue = paid_orders.aggregate(total=Sum('total'))['total'] or 0
    total_orders = paid_orders.count()
    avg_order_value = paid_orders.aggregate(avg=Avg('total'))['avg'] or 0
    total_customers = User.objects.filter(orders__isnull=False).distinct().count()

    last_30_days = timezone.now() - timedelta(days=30)
    recent_orders = paid_orders.filter(created_at__gte=last_30_days)
    recent_revenue = recent_orders.aggregate(total=Sum('total'))['total'] or 0
    recent_orders_count = recent_orders.count()

    status_breakdown = Order.objects.values('status').annotate(count=Count('id')).order_by('-count')

    top_products = (
        OrderItem.objects.filter(order__payment_status='paid')
        .values('product__name')
        .annotate(total_sold=Sum('quantity'), revenue=Sum('subtotal'))
        .order_by('-total_sold')[:5]
    )

    recent_order_list = Order.objects.order_by('-created_at')[:10]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'total_customers': total_customers,
        'recent_revenue': recent_revenue,
        'recent_orders_count': recent_orders_count,
        'status_breakdown': status_breakdown,
        'top_products': top_products,
        'recent_order_list': recent_order_list,
    }
    return render(request, 'admin/dashboard.html', context)