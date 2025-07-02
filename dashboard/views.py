from django.shortcuts import render, get_object_or_404, redirect
from management.models import JobOpening
from .forms import JobApplicationForm
from django.contrib.auth.decorators import login_required
from accounts.utils import phone_number_required
from accounts.models import CustomUser
from donation.models import Donation
from django.db.models import Sum

def pyramid_users(user):
    community = list(user.getCommunity())
    rows = []
    i = 0
    row_length = 1
    while i < len(community):
        rows.append(community[i:i+row_length])
        i += row_length
        row_length *= 2
    return rows


@login_required(login_url = 'login')
@phone_number_required
def dashboard(request):
    user = request.user

    if not user.is_donated:
        return redirect('/donate/')
    
    # Calculate donation metrics
    donations = Donation.objects.filter(user=user).aggregate(
        total_donated=Sum('amount')
    )
    total_donated = donations['total_donated'] or 0
    
    # Calculate impact metrics
    trees_planted = round(float(total_donated) / 100, 2)  # ₹100 = 1 tree
    total_co2 = round(trees_planted * 20, 1)  # 20kg CO2 per tree
    oxygen_produced = round(trees_planted * 118, 1)  # 118kg O2 per tree
    jobs_created = round(float(total_donated) / 5000, 1)  # ₹5000 = 1 day employment
    
    # Get referral data
    referrals = user.referrals.all()
    total_referrals = referrals.count()
    
    donations = Donation.objects.filter(user=user)
    context = {
        'donations': donations,
        'total_donated': total_donated,
        'total_trees': trees_planted,
        'total_co2': total_co2,
        'oxygen_produced': oxygen_produced,
        'jobs_created': jobs_created,
        'total_referrals': total_referrals,
        'referrals': referrals,
        'user_rows': pyramid_users(request.user),
    }
    
    return render(request, 'dashboard/dashboard.html', context)


def apply_job(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.save()
            return render(request, 'management/application-success.html')
    else:
        form = JobApplicationForm()

    return render(request, 'management/apply_form.html', {'form': form})
