from django.urls import path
from .views import *

urlpatterns = [
    path('', customer_search),
    path('hotel/<int:hotel_id>/', hotel_detail),
    path('room/<int:room_id>/', room_select),
    path('booking/details/', booking_details),
]
