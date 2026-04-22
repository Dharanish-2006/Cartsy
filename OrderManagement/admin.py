from django.contrib import admin
from .models import Order, OrderItem, Payment, Notification, NotificationLog

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("product", "quantity", "price")
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ("id", "user", "total_amount", "payment_method", "payment_status", "status", "created_at")
    list_filter   = ("status", "payment_method", "payment_status")
    search_fields = ("user__username", "user__email", "full_name")
    readonly_fields = ("created_at", "razorpay_order_id")
    list_editable = ("status",)
    ordering      = ("-created_at",)
    inlines       = [OrderItemInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ("order", "amount", "status", "razorpay_order_id", "created_at")
    list_filter   = ("status",)
    readonly_fields = ("razorpay_order_id", "razorpay_payment_id", "razorpay_signature", "created_at")
    ordering      = ("-created_at",)