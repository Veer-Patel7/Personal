from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="super_dashboard"),
    
    #owner login approval
    path('owners/', views.owners, name="owners"),
    path('approve-owner/<int:user_id>/', views.approve_owner),
    path('disable-owner/<int:user_id>/', views.disable_owner),
    path('enable-owner/<int:user_id>/', views.enable_owner),
    
    #hotel register approval
    path('hotels/', views.hotels_approve),
    path('approve-hotel/<int:hotel_id>/', views.approve_hotel),
    path('block-hotel/<int:hotel_id>/', views.block_hotel),
    path('reject-hotel/<int:hotel_id>/', views.reject_hotel),





]
