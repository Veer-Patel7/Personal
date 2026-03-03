from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .utils import generate_otp
from django.contrib.auth.decorators import login_required
from hotels.models import Hotel
# from .forms import SuperAdminLoginForm, UserLoginForm, UserRegistrationForm, ForgotPasswordForm, OTPVerificationForm, SetNewPasswordForm
from .form import ForgotPasswordForm, OTPVerificationForm, SetNewPasswordForm

# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# from django.urls import reverse







User = get_user_model()


# ========================== CUSTOMER LOGIN ==========================
def customer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return redirect("accounts:auth")

        if user.role != "customer":
            messages.error(request, "This is not a customer account")
            return redirect("accounts:auth")

        if not user.is_verified:
            messages.error(request, "Please verify OTP first")
            return redirect("accounts:auth")

        # ✅ LOGIN FIRST
        login(request, user)

        # ✅ THEN HANDLE NEXT
        next_url = request.GET.get("next") or request.POST.get("next")
        if next_url:
            return redirect(next_url)

        messages.success(request, "Customer login successful")
        return redirect("customer:home")

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


    return render(request, "accounts/hotel_login.html")

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

    return render(request, "accounts/super_login.html")

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

    return render(request, "accounts/hotel_signup.html")

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

    return render(request, "customer/verify.html", {"email": email})

# ========================== LOGOUT ==========================
def user_logout(request):
    logout(request)
    return redirect("/")

def auth_view(request):
    return render(request, "customer/auth.html")

# ========================== FORGOT PASSWORD ==========================
def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email)

                otp = generate_otp()
                user.otp = otp
                user.save()

                # ✅ VERY IMPORTANT
                request.session["reset_email"] = email

                send_mail(
                    "Password Reset OTP",
                    f"Your OTP is {otp}",
                    settings.EMAIL_HOST_USER,
                    [email],
                )

                return redirect("accounts:verify_reset_otp")

            except User.DoesNotExist:
                form.add_error("email", "Email not registered")
    else:
        form = ForgotPasswordForm()

    return render(request, "accounts/forgotpassword.html", {"form": form})

# ========================== VERIFY RESET OTP ==========================
def verify_reset_otp(request):
    email = request.session.get("reset_email")

    if not email:
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        form = OTPVerificationForm(request.POST)

        if form.is_valid():
            entered_otp = form.cleaned_data["otp"]

            user = User.objects.get(email=email)

            if user.otp == entered_otp:
                return redirect("accounts:set_new_password")
            else:
                form.add_error("otp", "Invalid OTP")
    else:
        form = OTPVerificationForm()

    return render(request, "accounts/verify_reset_otp.html", {"form": form})

# ========================== SET NEW PASSWORD ==========================
def set_new_password(request):
    email = request.session.get("reset_email")

    if not email:
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data["password"]

            user = User.objects.get(email=email)

            user.set_password(password)
            user.otp = ""
            user.save()

            # clear session
            del request.session["reset_email"]

            if user.role == "customer":
                return redirect("accounts:customer_login")
            elif user.role == "hotel_admin":
                return redirect("accounts:hotel_login")
            elif user.role == "super_admin":
                return redirect("accounts:super_login")
    else:
        form = SetNewPasswordForm()

    return render(request, "accounts/set_new_password.html", {"form": form})

# # ========================== FORGOT PASSWORD ==========================
# def customer_forgot_password(request):
#     if request.method == "POST":
#         email = request.POST.get("email")

#         try:
#             user = User.objects.get(email=email)

#             # ✅ ROLE CHECK
#             if user.role == "customer" and user.is_verified:

#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 token = default_token_generator.make_token(user)

#                 reset_link = request.build_absolute_uri(
#                     reverse("accounts:customer_reset_password", args=[uid, token])
#                 )

#                 send_mail(
#                     "Reset Your Password",
#                     f"Click the link to reset password:\n{reset_link}",
#                     settings.EMAIL_HOST_USER,
#                     [email],
#                     fail_silently=False,
#                 )
            
#         except User.DoesNotExist:
#             pass

#         messages.success(request, "Password reset link sent to your email")
#         return redirect("accounts:auth")



#     return render(request, "customer/forgot_password.html")

# # ========================== RESET PASSWORD ==========================
# def customer_reset_password(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except:
#         user = None

#     if user and default_token_generator.check_token(user, token):

#         if user.role != "customer":
#             messages.error(request, "Unauthorized access.")
#             return redirect("accounts:auth")

#         if request.method == "POST":
#             password = request.POST.get("password")
#             confirm = request.POST.get("confirm_password")

#             if password != confirm:
#                 messages.error(request, "Passwords do not match")
#                 return redirect(request.path)

#             user.set_password(password)
#             user.save()

#             messages.success(request, "Password reset successful")
#             return redirect("accounts:auth")

#         return render(request, "customer/reset_password.html")

#     messages.error(request, "Invalid or expired link")
#     return redirect("accounts:auth")