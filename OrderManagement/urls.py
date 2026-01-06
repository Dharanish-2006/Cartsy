from django.urls import path
from Inventory.views import *
from .views import *
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("new/", views.product_create, name="product_create"),
    path("<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("razorpay/create/", create_razorpay_order, name="create_razorpay_order"),
    path("razorpay/verify/", verify_payment, name="verify_payment"),
    path("success/", views.order_success, name="order_success"),
    path("cod/create/", views.create_cod_order, name="create_cod_order"),

]
