from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.utils import phone_number_required
from django.db.models import Sum


# Create your views here.
@login_required(login_url = 'login')
@phone_number_required
def earning_dashboard(request):
    user = request.user

    if not user.registration_fee_paid:
        return redirect('/donate/complete-registration/')
    
    if not request.user.has_usable_password():
        return redirect("set_password")
    
    context = {
    }
    
    return render(request, 'earning/dashboard.html', context)

