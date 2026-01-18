from django.urls import path
from .views import *

# urlpatterns = [
#     path('', Home, name="home"),
#     path('about/',about),
#     path('service/',service),
#     path('contact/',contact),
#     path('cart/',cart,name="cart"),
#     path("cart/remove/<int:pk>/", remove_from_cart, name="remove_from_cart"),
#     path('myorder/',order,name="orders"),
#     path('cancelorder/<int:id>/',delete_product,name='delete_product'),
#     path('updateorder/<int:id>/',update_product,name='update_product'),
#     path('product/<int:pk>/', product_detail, name='product_detail'),
#     path("checkout/", checkout, name="checkout"),
#     path('myorder/<int:pk>/',order_detail, name='order_detail'),
#     path("cart/increase/<int:item_id>/", increase_quantity, name="increase_quantity"),
#     path("cart/decrease/<int:item_id>/", decrease_quantity, name="decrease_quantity"),
# ]

urlpatterns = [
    path("api/home/", HomeAPI.as_view()),
    path("api/products/<int:pk>/", ProductDetailAPI.as_view()),

    path("api/cart/", CartAPI.as_view()),
    path("api/cart/update/", UpdateCartQuantity.as_view()),

    path("api/orders/", OrdersAPI.as_view()),
]
