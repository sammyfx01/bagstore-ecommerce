from django.contrib import admin
from .models import Coupon, Order, OrderItem


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active', 'valid_until')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'unit_price', 'subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status')
    list_editable = ('status',)
    search_fields = ('customer__username', 'full_name', 'payment_reference')
    inlines = [OrderItemInline]
    readonly_fields = ('customer', 'subtotal', 'discount', 'total', 'payment_status', 'payment_reference', 'created_at', 'updated_at')

    actions = ['mark_processing', 'mark_packed', 'mark_shipped', 'mark_out_for_delivery', 'mark_delivered']

    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_processing.short_description = "Mark selected orders as Processing"

    def mark_packed(self, request, queryset):
        queryset.update(status='packed')
    mark_packed.short_description = "Mark selected orders as Packed"

    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_shipped.short_description = "Mark selected orders as Shipped"

    def mark_out_for_delivery(self, request, queryset):
        queryset.update(status='out_for_delivery')
    mark_out_for_delivery.short_description = "Mark selected orders as Out for Delivery"

    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_delivered.short_description = "Mark selected orders as Delivered"