from django.db import models
from accounts.models import User


class Hotel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel_name = models.CharField(max_length=100)
    property_type = models.CharField(max_length=50)
    star_rating = models.IntegerField()
    description = models.TextField()

    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    address = models.TextField()
    pincode = models.CharField(max_length=10)

    is_approved = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.hotel_name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=20)
    room_number = models.CharField(max_length=10)
    room_size = models.IntegerField()
    max_guest = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, default="available")

    def __str__(self):
        return f"{self.hotel.hotel_name} - {self.room_number}"
