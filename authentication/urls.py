from django.urls import path
from .views import *

urlpatterns = [
    path('',CustomLoginView.as_view(),name="login"),
    path("signup/", signup, name="signup"),
    path('logout/',LogoutUser),
    path("verify-otp/", verify_otp, name="verify_otp"),
]
