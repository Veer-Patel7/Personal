from django.db import models
from accounts.models import User
from hotels.models import Hotel, RoomType
from django.core.exceptions import ValidationError

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room = models.ForeignKey(RoomType, on_delete=models.CASCADE)

    checkin_date = models.DateField()
    checkout_date = models.DateField()
    
    # aadhaar_id = models.CharField(max_length=20)
    total_guests = models.SmallIntegerField(null=True, blank=True)
    adults = models.SmallIntegerField(null=True, blank=True)
    children = models.SmallIntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, default="cash")
    booking_status = models.CharField(max_length=20, default="confirm")
    
    cancel_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if self.total_guests != self.adults + self.children:
            raise ValidationError("Total guests must equal adults + children")

        if self.checkin_date >= self.checkout_date:
            raise ValidationError("Checkout date must be after checkin date")

    def __str__(self):
        return f"{self.user.email} - {self.room}"
