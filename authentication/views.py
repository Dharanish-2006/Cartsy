from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailOTP, User
from OrderManagement.utils.otp import generate_otp
from django.utils import timezone
from datetime import timedelta


class SignupAPI(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password")
        username = request.data.get("username")

        if not email or not password or not username:
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            is_active=False
        )

        otp = generate_otp()

        EmailOTP.objects.update_or_create(
            user=user,
            defaults={"otp": otp}
        )

        send_mail(
            subject="Your OTP – CARTSY",
            message=f"Your OTP is {otp}. Valid for 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent successfully"})
class LoginAPI(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=401)

        if not user.is_active:
            return Response({"error": "Account not verified"}, status=403)

        user = authenticate(username=user.username, password=password)

        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })
class VerifyOTP(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        entered_otp = request.data.get("otp")

        if not email or not entered_otp:
            return Response({"error": "Email and OTP required"}, status=400)

        try:
            user = User.objects.get(email=email)
            otp_obj = EmailOTP.objects.get(user=user)
        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            return Response({"error": "Invalid request"}, status=400)

        if timezone.now() - otp_obj.created_at > timedelta(minutes=5):
            otp_obj.delete()
            return Response({"error": "OTP expired"}, status=400)

        if otp_obj.otp != entered_otp:
            return Response({"error": "Invalid OTP"}, status=400)

        user.is_active = True
        user.save()
        otp_obj.delete()

        return Response({"message": "Account verified successfully"})
