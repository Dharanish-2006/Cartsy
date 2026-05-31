from django.urls import path
from Inventory.views import *
from .views import *
from . import views

urlpatterns = [
    path("razorpay/create/", create_razorpay_order, name="create_razorpay_order"),
    path("razorpay/verify/", verify_payment, name="verify_payment"),
    path("cod/create/", views.create_cod_order, name="create_cod_order"),
]
