from django.urls import path
from .views import *

urlpatterns = [
    path("signup/", SignupAPI.as_view()),
    path("login/", LoginAPI.as_view()),
    path("verify-otp/", VerifyOTP.as_view()),
]

