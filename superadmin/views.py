from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from hotels.models import Hotel
from django.core.mail import send_mail
from django.conf import settings
from bookings.models import Booking



User = get_user_model()


@login_required(login_url="/super/")
def dashboard(request):
    return render(request, "superadmin/dashboard.html")



#--------- hotel owner login req approve ---------

@login_required(login_url="/super/")
def owners(request):
    if request.user.role != "super_admin":
        return HttpResponse("Unauthorized")

    owners = User.objects.filter(role="hotel_admin")
    return render(request, "superadmin/owners.html", {"owners": owners})


#  APPROVE OWNER (pending → active)
@login_required(login_url="/super/")
def approve_owner(request, user_id):
    owner = User.objects.get(id=user_id)
    owner.is_active = True
    owner.save()
    return redirect("/super/owners/")


#  DISABLE OWNER
@login_required(login_url="/super/")
def disable_owner(request, user_id):
    owner = User.objects.get(id=user_id)
    owner.is_active = False
    owner.save()
    return redirect("/super/owners/")


#  ENABLE OWNER
@login_required(login_url="/super/")
def enable_owner(request, user_id):
    owner = User.objects.get(id=user_id)
    owner.is_active = True
    owner.save()
    return redirect("/super/owners/")


#-------  hotel registration ----------

@login_required(login_url="/super/")
def hotels_approve(request):
    if request.user.role != "super_admin":
        return HttpResponse("Unauthorized")

    hotels = Hotel.objects.all()
    return render(request, "superadmin/hotels.html", {"hotels": hotels})


@login_required(login_url="/super/")
def approve_hotel(request, hotel_id):
    h = Hotel.objects.get(id=hotel_id)
    h.status = "approved"
    h.save()
    return redirect("/super/hotels/")


@login_required(login_url="/super/")
def block_hotel(request, hotel_id):
    h = Hotel.objects.get(id=hotel_id)
    h.status = "blocked"
    h.save()
    return redirect("/super/hotels/")

#------reject hotel with reason mail--------
@login_required(login_url="/super/")
def reject_hotel(request, hotel_id):

    if request.user.role != "super_admin":
        return HttpResponse("Unauthorized")

    hotel = Hotel.objects.get(id=hotel_id)

    if request.method == "POST":
        reason = request.POST.get("reason")

        hotel.status = "rejected"
        hotel.reject_reason = reason
        hotel.save()

        # 📧 EMAIL OWNER
        send_mail(
            "Hotel Rejected",
            f"Your hotel '{hotel.hotel_name}' was rejected.\nReason: {reason}",
            settings.EMAIL_HOST_USER,
            [hotel.owner.email],
            fail_silently=False,
        )

        return redirect("/super/hotels/")

    return render(request, "superadmin/reject_form.html", {"hotel": hotel})


#--------Booking manage---------

@login_required(login_url="/super/")
def bookings_manage(request):

    if request.user.role != "super_admin":
        return HttpResponse("Unauthorized")

    bookings = Booking.objects.all().order_by("-id")

    return render(request, "superadmin/bookings.html", {"bookings": bookings})

@login_required(login_url="/super/")
def update_booking(request, booking_id):
    if request.user.role != "super_admin":
        return HttpResponse("Unauthorized")

    b = Booking.objects.get(id=booking_id)

    if request.method == "POST":

        # SAFE DATE UPDATE
        checkin = request.POST.get("checkin_date")
        checkout = request.POST.get("checkout_date")

        if checkin:
            b.checkin_date = checkin

        if checkout:
            b.checkout_date = checkout

        # 🔴 FORCE CANCEL
        if request.POST.get("force_cancel"):
            reason = request.POST.get("reason")

            b.booking_status = "cancelled"
            b.cancel_reason = reason
            b.save()

            # EMAIL → customer
            send_mail(
                "Booking Cancelled",
                f"Your booking #{b.id} was cancelled.\nReason: {reason}",
                settings.EMAIL_HOST_USER,
                [b.user.email],
                fail_silently=True,
            )

            # EMAIL → hotel owner
            send_mail(
                "Booking Cancelled by Super Admin",
                f"Booking #{b.id} cancelled.\nReason: {reason}",
                settings.EMAIL_HOST_USER,
                [b.hotel.owner.email],
                fail_silently=True,
            )

            return redirect("/super/bookings/")

        # 🟢 NORMAL STATUS UPDATE
        status = request.POST.get("status")
        if status:
            b.booking_status = status

        b.save()
        return redirect("/super/bookings/")
