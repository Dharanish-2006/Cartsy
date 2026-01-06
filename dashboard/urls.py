from django.urls import path
from .views import *

urlpatterns = [
    path('',dashboard_view),
    path("product/<int:pk>/",product_detail),
]
