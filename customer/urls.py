from django.urls import include, path
from .views import *

urlpatterns = [
    # Customer homepage
    path('', customer_search, name="home"),

    # Hotel and Room details
    path('hotel/<int:hotel_id>/', hotel_detail, name="hotel_detail"),
    path('room/<int:room_id>/', room_select, name="room_select"),

    # Booking details
    path('booking/details/', booking_details, name="booking_details"),

    # Review add
    path('add-review/<int:hotel_id>/', add_review, name="add_review"),
]
