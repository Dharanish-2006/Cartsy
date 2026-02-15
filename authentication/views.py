from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import EmailOTP, User
from OrderManagement.utils.otp import generate_otp


def send_otp_email(email, otp):
    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}",
        "Content-Type": "application/json",
    }

    data = {
        "from": "Cartsy <onboarding@resend.dev>",  # FREE account must use this
        "to": [email],
        "subject": "Your OTP – CARTSY",
        "html": f"<h2>Your OTP is {otp}</h2><p>Valid for 5 minutes.</p>",
    }

    response = requests.post(url, headers=headers, json=data)
    print("Resend Response:", response.status_code, response.text)
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

        send_otp_email(email, otp)

        return Response(
            {"message": "OTP sent successfully"},
            status=status.HTTP_200_OK
        )


class LoginAPI(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "Account not verified"},
                status=status.HTTP_403_FORBIDDEN
            )

        user = authenticate(username=user.username, password=password)
        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "message": "Login successful"
            },
            status=status.HTTP_200_OK
        )


class VerifyOTP(APIView):
    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        entered_otp = request.data.get("otp")

        if not email or not entered_otp:
            return Response(
                {"error": "Email and OTP required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            otp_obj = EmailOTP.objects.get(user=user)
        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            return Response(
                {"error": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() - otp_obj.created_at > timedelta(minutes=5):
            otp_obj.delete()
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.otp != entered_otp:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = True
        user.save()
        otp_obj.delete()

        return Response(
            {"message": "Account verified successfully"},
            status=status.HTTP_200_OK
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def LogoutAPI(request):
    return Response(
        {"message": "Logged out successfully"},
        status=status.HTTP_200_OK
    )