from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="super_dashboard"),
    path('owners/', views.owners, name="owners"),

    path('approve-owner/<int:user_id>/', views.approve_owner),
    path('disable-owner/<int:user_id>/', views.disable_owner),
    path('enable-owner/<int:user_id>/', views.enable_owner),
]
