from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.hotel_dashboard, name="hotel_dashboard"),
]
