from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required(login_url="/super/")
def dashboard(request):
    return render(request, "superadmin/dashboard.html")


@login_required(login_url="/super/")
def owners(request):
    if request.user.role != "super_admin":
        return HttpResponse("Unauthorized")

    owners = User.objects.filter(role="hotel_admin")
    return render(request, "superadmin/owners.html", {"owners": owners})


# 🟢 APPROVE OWNER (pending → active)
@login_required(login_url="/super/")
def approve_owner(request, user_id):
    owner = User.objects.get(id=user_id)
    owner.is_active = True
    owner.save()
    return redirect("/super/owners/")


# 🔴 DISABLE OWNER
@login_required(login_url="/super/")
def disable_owner(request, user_id):
    owner = User.objects.get(id=user_id)
    owner.is_active = False
    owner.save()
    return redirect("/super/owners/")


# 🟢 ENABLE OWNER
@login_required(login_url="/super/")
def enable_owner(request, user_id):
    owner = User.objects.get(id=user_id)
    owner.is_active = True
    owner.save()
    return redirect("/super/owners/")
