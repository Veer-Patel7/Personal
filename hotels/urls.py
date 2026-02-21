from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('dashboard/<int:hotel_id>/', views.hotel_dashboard, name='hotel_dashboard'),
    path('register/', views.register_hotel, name="register_hotel"),
    
    # REVIEW
    
    path("reviews/", views.hotel_reviews),
    path("request-delete/<int:id>/", views.request_delete_review),
]
