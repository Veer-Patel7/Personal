from django.db import models
from accounts.models import User


class Hotel(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    hotel_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100,null=True, blank=True)

    id_proof1 = models.FileField(upload_to="hotel_docs/",null=True, blank=True)
    id_proof2 = models.FileField(upload_to="hotel_docs/",null=True, blank=True)

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("blocked", "Blocked"),
        ("rejected", "Rejected"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    reject_reason = models.TextField(null=True, blank=True)
    
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
