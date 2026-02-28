from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from hotels.models import Hotel, RoomType
from bookings.models import Booking
from accounts.models import User
from reviews.models import Review
from django.db.models import Min, Max
@login_required(login_url="/login/")
def dashboard(request):
    return render(request, "customer/dashboard.html")

def customer_search(request):
    hotels = Hotel.objects.all()

    location = request.POST.get("location")

    if location:
        hotels = hotels.filter(city__icontains=location)
        
    hotels = Hotel.objects.annotate(
    min_price=Min("rooms__price_per_night"),
    max_price=Max("rooms__price_per_night"))

    # Add min and max price from related rooms
    # hotels = hotels.annotate(
    #     min_price=Min("rooms__category__price_per_night"),
    #     max_price=Max("rooms__category__price_per_night")
    # )
        
    return render(request, "customer/search.html", {"hotels": hotels})

def search_results(request):
    location = request.GET.get("location")
    persons = request.GET.get("persons")
    
    rooms = RoomType.objects.select_related('hotel')

    if location:
        rooms = rooms.filter(hotel__city__icontains=location)
    
    if persons:
        rooms = rooms.filter(max_guest__gte=persons)
        
    # rooms = rooms.filter(max_guest)

    # if request.method == "POST":
    #     city = request.POST.get("city")
    #     check_in = request.POST.get("check_in")
    #     check_out = request.POST.get("check_out")

    #     # For simplicity, we are not filtering based on availability in this example
    #     hotels = Hotel.objects.filter(city__icontains=city)
    return render(request, "customer/search_results.html", {"rooms":rooms})

    # return redirect("hotel_detail")

def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    rooms = RoomType.objects.filter(hotel=hotel)

    return render(request, "customer/hotel_detail.html", {
        "hotel": hotel,
        "rooms": rooms   # ✔ plural name
    })

def room_select(request, room_id):
    return render(request, "customer/room_select.html", {"room_id": room_id})

# @login_required(login_url="/login/")
def booking_details(request, hotel_id, room_id):
    hotel = get_object_or_404(Hotel,id=hotel_id)
    room = get_object_or_404(RoomType, id=room_id)
    
    if request.method == "POST":
        
        request.session["booking_data"] = {
            "hotel_id": hotel.id,
            "room_id": room.id,
            "check_in_date": request.POST.get("checkin_date"),
            "check_out_date": request.POST.get("checkout_date"),
            "guests": request.POST.get("guests"),
            "aadhaar_no": request.POST.get("aadhaar_no"),
            "payment": request.POST.get("payment"),
        }

        return redirect("customer:confirm_booking")
    
    return render(request, "customer/booking_details.html",{"hotel":hotel, "room":room})

@login_required
def confirm_booking(request):
    data =request.session.get("booking_data")
    if not data:
        return redirect("customer:home")
    
    hotel = Hotel.objects.get(id=data["hotel_id"])
    room = RoomType.objects.get(id=data["room_id"])
    
    if request.method == "POST":

        Booking.objects.create(
            user=request.user,
            hotel=hotel,
            room=room,
            checkin_date=data["check_in_date"],
            checkout_date=data["check_out_date"],
            aadhaar_id=data["aadhaar_no"],
            payment_method=data["payment"],
        )

        del request.session["booking_data"]
        return redirect("customer:success")
    
    return render(request, "customer/confirm_booking.html", {"data":data, "room":room, "hotel":hotel})

def booking_success(request):
    return render(request, "customer/success.html")

@login_required(login_url="/login/")
def add_review(request, hotel_id):

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        recommend = request.POST.get("recommend")

        Review.objects.create(
            hotel_id=hotel_id,
            user=request.user,
            rating=rating,
            comment=comment,
            recommend=True if recommend == "yes" else False
        )

        return redirect("/")

    return render(request, "customer/add_review.html")