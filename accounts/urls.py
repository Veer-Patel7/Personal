from django.urls import path
from . import views

urlpatterns = [
    # customer
    path('login/', views.customer_login, name="customer_login"),
    path('signup/', views.customer_signup, name="customer_signup"),

    # hotel admin
    path('hotel/login/', views.hotel_login, name="hotel_login"),
    path('hotel/signup/', views.hotel_signup, name="hotel_signup"),

    # super admin login
    path('super/', views.super_login, name="super_login"),

    # otp
    path('verify/', views.verify, name="verify"),

    # logout
    path('logout/', views.user_logout, name="logout"),
]
