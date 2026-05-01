import os
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
from django.conf import settings

from threading import Thread

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def send_otp_email(email, otp):
    subject = "Email verification for your SVS Collections account"

    html_content = f"""
    <html>
    <body style="margin:0; padding:0; background:#0B0B1A; font-family:Arial, sans-serif; color:white;">
        
        <div style="max-width:500px; margin:40px auto; padding:30px; background:#111126; border-radius:12px; text-align:center;">
            
            <h1 style="
                background: linear-gradient(90deg, #7F5AF0, #FF6AC1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size:28px;
                margin-bottom:10px;
            ">
                SVS Collections
            </h1>

            <p style="color:#aaa; margin-bottom:20px;">
                Verify your email to continue
            </p>

            <div style="
                background:#1A1A2E;
                padding:20px;
                border-radius:10px;
                margin:20px 0;
            ">
                <p style="margin:0; color:#bbb;">Your verification code</p>
                <h2 style="font-size:32px; margin:10px 0; letter-spacing:4px;">
                    {otp}
                </h2>
            </div>

            <p style="color:#888; font-size:14px;">
                This code expires in 5 minutes.
            </p>

            <a href="#" style="
                display:inline-block;
                margin-top:20px;
                padding:12px 24px;
                border-radius:8px;
                background: linear-gradient(90deg, #7F5AF0, #FF6AC1);
                color:white;
                text-decoration:none;
                font-weight:bold;
            ">
                Verify Account
            </a>

            <p style="margin-top:30px; font-size:12px; color:#666;">
                If you didn’t request this, ignore this email.
            </p>

        </div>

    </body>
    </html>
    """

    def _send():
        try:
            payload = {
                "sender": {
                    "name": "SVS Collections",
                    "email": "dharanishwar.2006@gmail.com",
                },
                "to": [{"email": email}],
                "subject": subject,
                "htmlContent": html_content,
            }

            headers = {
                "accept": "application/json",
                "api-key": settings.BREVO_API_KEY,
                "content-type": "application/json",
            }

            resp = requests.post(BREVO_URL, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()

            import logging
            logging.getLogger(__name__).info(f"Using API key: {settings.BREVO_API_KEY[:10]}...")

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"OTP email failed for {email}: {e}")

    Thread(target=_send, daemon=True).start()
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

        user = authenticate(request,username=user.username, password=password)
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