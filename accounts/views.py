from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .utils import generate_otp
from django.contrib.auth.decorators import login_required
from hotels.models import Hotel


User = get_user_model()


# ========================== CUSTOMER LOGIN ==========================
def customer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return redirect("auth")

        if user.role != "customer":
            messages.error(request, "This is not a customer account")
            return redirect("auth")

        if not user.is_verified:
            messages.error(request, "Please verify OTP first")
            return redirect("auth")

        login(request, user)
        messages.success(request, "Customer login successful")

        next_url = request.GET.get("next")
        if next_url:
            return redirect(next_url)

        return redirect("customer:booking_details")

    return render(request, "customer/auth.html")


# ========================== HOTEL LOGIN ==========================
def hotel_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return redirect("hotel_login")

        if user.role != "hotel_admin":
            messages.error(request, "This is not a hotel admin account")
            return redirect("hotel_login")

        if not user.is_verified:
            messages.error(request, "Please verify OTP first")
            return redirect("hotel_login")

        login(request, user)
        messages.success(request, "Hotel admin login successful")
        hotel = Hotel.objects.filter(owner=user).first()

        if hotel:
            return redirect('hotels:hotel_dashboard', hotel_id=hotel.id)
        else:
            return redirect('/hotel/register/')


    return render(request, "hotel_login.html")


# ========================== SUPER ADMIN LOGIN ==========================
def super_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return redirect("/super/")

        if user.role != "super_admin":
            messages.error(request, "Not a super admin account")
            return redirect("/super/")

        login(request, user)
        messages.success(request, "Super admin login successful")
        return redirect("super_dashboard")

    return render(request, "super_login.html")


# ========================== CUSTOMER SIGNUP WITH OTP ==========================

def customer_signup(request):

    if request.method == "POST":
        first = request.POST.get("first_name")
        last = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            # return redirect("customer_signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            # return redirect("customer_signup")
        otp = generate_otp()

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first,
            last_name=last,
            role="customer",
            otp=otp,
            is_active=False
        )

        send_mail(
            "OTP Verification",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
        )

        messages.success(request, "OTP sent to your email")
        return redirect(f"/verify/?email={email}",user="user")
        
    return render(request, "customer_signup")


# ========================== HOTEL ADMIN SIGNUP WITH OTP ==========================
def hotel_signup(request):

    if request.method == "POST":
        first = request.POST.get("first_name")
        last = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("hotel_signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("hotel_signup")

        otp = generate_otp()

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first,
            last_name=last,
            role="hotel_admin",
            otp=otp,
            is_active=False
        )

        send_mail(
            "OTP Verification",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
        )

        messages.success(request, "OTP sent to your email")
        return redirect(f"/verify/?email={email}")

    return render(request, "hotel_signup.html")


# ========================== VERIFY OTP ==========================
def verify(request):

    email = request.GET.get("email")

    if request.method == "POST":
        otp = request.POST.get("otp")

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User not found")
            return redirect("accounts:verify")

        if user.otp == otp:
            user.is_verified = True
            user.is_active = True
            user.otp = ""
            user.save()

            messages.success(request, "Account verified successfully")

            if user.role == "customer":
                return redirect("/login/")
            else:
                return redirect("/hotel/login/")

        messages.error(request, "Invalid OTP")

    return render(request, "verify.html", {"email": email})


# ========================== LOGOUT ==========================
def user_logout(request):
    logout(request)
    return redirect("/")

def auth_view(request):
    return render(request, "customer/auth.html")