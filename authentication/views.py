from .forms import SignUpForm
from django.core.mail import send_mail
from django.shortcuts import render,redirect
from django.contrib.auth import login,logout
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import EmailOTP,User
from OrderManagement.utils.otp import generate_otp
from .forms import SignUpForm
from django.utils import timezone
from datetime import timedelta

class CustomLoginView(LoginView):
    template_name = "login.html"
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_navbar"] = False
        return context
    template_name = "login.html"

def LogoutUser(request):
    logout(request)
    return(redirect('/'))

def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            user.save()

            otp = generate_otp()

            EmailOTP.objects.update_or_create(
                user=user,
                defaults={"otp": otp}
            )

            send_mail(
                subject="Your OTP – CARTSY",
                message=f"Your OTP is {otp}. Valid for 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            request.session["verify_user_id"] = user.id
            return redirect("verify_otp")
    else:
        form = SignUpForm()

    return render(request, "signup.html", {
        "form": form,
        "show_navbar": False
    })

def verify_otp(request):
    user_id = request.session.get("verify_user_id")
    if not user_id:
        return redirect("signup")

    user = User.objects.get(id=user_id)
    otp_obj = EmailOTP.objects.get(user=user)

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        if timezone.now() - otp_obj.created_at > timedelta(minutes=5):
            return render(request, "verify_otp.html", {
                "error": "OTP expired",
                "show_navbar": False
            })

        if entered_otp == otp_obj.otp:
            user.is_active = True
            user.save()
            otp_obj.delete()
            login(request, user)

            return redirect("home")

        return render(request, "verify_otp.html", {
            "error": "Invalid OTP",
            "show_navbar": False
        })

    return render(request, "verify_otp.html", {"show_navbar": False})
