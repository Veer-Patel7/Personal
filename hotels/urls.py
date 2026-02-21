from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('dashboard/<int:hotel_id>/', views.hotel_dashboard, name='hotel_dashboard'),
    path('register/', views.register_hotel, name="register_hotel"),
]
