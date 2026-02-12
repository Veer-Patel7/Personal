from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url="/hotel/login/")
def hotel_dashboard(request):
    return render(request, "hotel/dashboard.html")
