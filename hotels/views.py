from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Hotel
from reviews.models import Review


@login_required(login_url="/hotel/login/")
def hotel_dashboard(request, hotel_id):


    # approved hotel check
    approved_hotel = Hotel.objects.filter(owner=request.user, status="approved").first()

    if approved_hotel:
        return render(request, "hotels/hotel_dashboard.html", {"hotel": approved_hotel})

    # agar approved nahi hai → latest hotel check
    hotel = Hotel.objects.filter(owner=request.user).order_by("-id").first()

    if not hotel:
        return redirect("/hotel/register/")

    if hotel.status == "pending":
        return render(request, "hotels/waiting.html")

    if hotel.status == "rejected":
        return render(request, "hotels/rejected.html")

    if hotel.status == "blocked":
        return HttpResponse("Hotel Blocked")

    return redirect("/hotel/register/")

@login_required(login_url="/hotel/login/")
def register_hotel(request):

    user = request.user

    # check if already has hotel
    hotel = Hotel.objects.filter(owner=user).first()
    if hotel:
        return redirect('hotels:hotel_dashboard', hotel_id=hotel.id)

    if request.method == "POST":
        name = request.POST.get("hotel_name")
        location = request.POST.get("location")
        id1 = request.FILES.get("id1")
        id2 = request.FILES.get("id2")

        hotel = Hotel.objects.create(
            owner=user,
            hotel_name=name,
            location=location,
            id_proof1=id1,
            id_proof2=id2
        )

        return redirect('hotels:hotel_dashboard', hotel_id=hotel.id)

    return render(request, "hotels/register_hotel.html")

#----------review-------------

@login_required(login_url="/hotel/login/")
def hotel_reviews(request):

    reviews = Review.objects.filter(hotel__owner=request.user)

    return render(request, "hotels/reviews.html", {"reviews": reviews})


@login_required(login_url="/hotel/login/")
def request_delete_review(request, id):

    r = Review.objects.get(id=id)

    if r.hotel.owner != request.user:
        return HttpResponse("Unauthorized")

    r.status = "delete_request"
    r.save()

    return redirect("/hotel/reviews/")