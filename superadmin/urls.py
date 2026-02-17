from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="super_dashboard"),
    
    # OWNER LOGIN APPROVAL
    path('owners/', views.owners, name="owners"),
    path('approve-owner/<int:user_id>/', views.approve_owner),
    path('disable-owner/<int:user_id>/', views.disable_owner),
    path('enable-owner/<int:user_id>/', views.enable_owner),
    
    # HOTEL REGISTER APPROVAL
    path('hotels/', views.hotels_approve),
    path('approve-hotel/<int:hotel_id>/', views.approve_hotel),
    path('block-hotel/<int:hotel_id>/', views.block_hotel),
    path('reject-hotel/<int:hotel_id>/', views.reject_hotel),

    # BOOKING MANAGE
    path("bookings/", views.bookings_manage),
    path("update-booking/<int:booking_id>/", views.update_booking),




]
