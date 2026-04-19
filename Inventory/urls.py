from django.urls import path
from .views import *
urlpatterns = [
    path("api/home/",                    HomeAPI),
    path("api/products/<int:pk>/",       ProductDetailAPI.as_view()),
    path("api/cart/",                    CartAPI.as_view()),
    path("api/cart/update/",             UpdateCartQuantity.as_view()),
    path("api/orders/",                  OrdersAPI.as_view()),
    path("api/orders/create/",           CreateOrderAPI.as_view()),
    path("api/orders/razorpay/",         CreateRazorpayOrderAPI.as_view()),
    path("api/orders/razorpay/verify/",  VerifyPaymentAPI.as_view()),
    path("ping/",                        ping),
    path("api/admin/orders/", AdminOrderListAPI.as_view()),
    path("api/admin/orders/<int:pk>/", AdminOrderDetailAPI.as_view()),
    path("api/admin/orders/<int:pk>/status/", UpdateOrderStatusAPI.as_view()),
    path("api/admin/notifications/", AdminNotificationsAPI.as_view()),
    path("api/admin/notifications/<int:pk>/read/", MarkNotificationReadAPI.as_view()),
]