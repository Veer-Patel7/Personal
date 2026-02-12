from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Hotel

@login_required(login_url="/hotel/login/")
def hotel_dashboard(request):

    hotel = Hotel.objects.filter(owner=request.user).first()

    if not hotel:
        return redirect("/hotel/register/")

    if hotel.status != "approved":
        return render(request, "hotels/waiting.html")

    return render(request, "hotels/hotel_dashboard.html")


@login_required(login_url="/hotel/login/")
def register_hotel(request):

    if request.method == "POST":
        name = request.POST.get("hotel_name")
        location = request.POST.get("location")
        id1 = request.FILES.get("id1")
        id2 = request.FILES.get("id2")

        Hotel.objects.create(
            owner=request.user,
            hotel_name=name,
            location=location,
            id_proof1=id1,
            id_proof2=id2
        )

        return render(request, "hotels/waiting.html")

    return render(request, "hotels/register_hotel.html")