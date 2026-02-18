from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from hotels.models import Hotel
from accounts.models import User
from bookings.models import Booking
from payments.models import HotelCommission
from datetime import date, timedelta
from django.conf import settings




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

        # EMAIL OWNER
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

        # FORCE CANCEL
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

        # NORMAL STATUS UPDATE
        status = request.POST.get("status")
        if status:
            b.booking_status = status

        b.save()
        return redirect("/super/bookings/")

# ================= PAYMENTS DASHBOARD =================
@login_required(login_url="/super/")
def payments_dashboard(request):
    return render(request, "superadmin/payments_dashboard.html")


# ================= GENERATE COMMISSION =================
@login_required(login_url="/super/")
def generate_commission(request):

    # month select from form
    month = request.GET.get("month")

    if month:
        year, m = month.split("-")
        month = int(m)
        year = int(year)
    else:
        today = date.today()
        month = today.month
        year = today.year

    hotels = Hotel.objects.filter(status="approved")

    for h in hotels:

        bookings = Booking.objects.filter(
            hotel=h,
            booking_status="confirmed",
            checkin_date__month=month,
            checkin_date__year=year
        )

        total_revenue = sum([b.room.price_per_night for b in bookings])
        total_bookings = bookings.count()

        commission_percent = 10
        commission_amount = total_revenue * commission_percent / 100

        due_date = date.today() + timedelta(days=5)

        HotelCommission.objects.update_or_create(
            hotel=h,
            month=month,
            year=year,
            defaults={
                "total_bookings": total_bookings,
                "total_revenue": total_revenue,
                "commission_amount": commission_amount,
                "due_date": due_date,
                "status": "pending"
            }
        )

    return redirect("/super/payments/invoices/")


# ================= VIEW INVOICES =================
@login_required(login_url="/super/")
def commissions(request):

    invoices = HotelCommission.objects.all().order_by("-id")

    today = date.today()

    for i in invoices:

        # overdue check
        if i.status == "pending" and today > i.due_date:
            i.status = "overdue"
            i.penalty = i.commission_amount * 0.05
            i.save()

        # auto block after 5 days overdue
        if i.status == "overdue":
            if today > i.due_date + timedelta(days=5):
                i.hotel.status = "blocked"
                i.hotel.save()

    return render(request, "superadmin/commissions.html", {"data": invoices})


# ================= MARK PAID =================
@login_required(login_url="/super/")
def mark_paid(request, id):

    p = HotelCommission.objects.get(id=id)
    p.status = "paid"
    p.penalty = 0
    p.save()

    return redirect("/super/payments/invoices/")


# ================= SEND PAYMENT REMINDER =================
@login_required(login_url="/super/")
def send_payment_mail(request, id):

    p = HotelCommission.objects.get(id=id)

    send_mail(
        "Commission Payment Due",
        f"""
        Hotel: {p.hotel.hotel_name}
        Amount: ₹{p.commission_amount}
        Due date: {p.due_date}

        Please pay within 5 days.
        """,
        settings.EMAIL_HOST_USER,
        [p.hotel.owner.email],
        fail_silently=True,
    )

    return redirect("/super/payments/invoices/")

#--------CUSTOMER MANAGE---------

@login_required(login_url="/super/")
def customers_manage(request):

    if request.user.role != "super_admin":
        return HttpResponse("Unauthorized")

    customers = User.objects.filter(role="customer")

    data = []

    for c in customers:
        total = Booking.objects.filter(user=c).count()
        data.append({
            "obj": c,
            "total": total
        })

    return render(request, "superadmin/customers.html", {"data": data})

#Blacklist customer
@login_required(login_url="/super/")
def blacklist_customer(request, user_id):

    c = User.objects.get(id=user_id)
    c.is_active = False
    c.save()

    return redirect("/super/customers/")

#Unblock customer
@login_required(login_url="/super/")
def unblock_customer(request, user_id):

    c = User.objects.get(id=user_id)
    c.is_active = True
    c.save()

    return redirect("/super/customers/")

