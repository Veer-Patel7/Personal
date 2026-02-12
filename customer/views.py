from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url="/login/")
def dashboard(request):
    return render(request, "customer/dashboard.html")

def customer_search(request):
    return render(request, "customer/search.html")

def hotel_detail(request, hotel_id):
    return render(request, "customer/hotel_detail.html", {"hotel_id": hotel_id})

def room_select(request, room_id):
    return render(request, "customer/room_select.html", {"room_id": room_id})

@login_required(login_url="/login/")
def booking_details(request):
    return render(request, "customer/booking_details.html")
