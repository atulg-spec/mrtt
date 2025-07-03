from django.shortcuts import render, get_object_or_404, redirect
from management.models import JobOpening
from .forms import JobApplicationForm
from django.contrib.auth.decorators import login_required
from accounts.utils import phone_number_required
from accounts.models import CustomUser
from django.core.paginator import Paginator  # Add this import
from donation.models import Donation, Payments
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


@login_required(login_url='login')
@phone_number_required
def my_donations(request):
    # Get all donations for the current user
    donations = Donation.objects.filter(user=request.user)
    
    # Calculate total donations
    total_donations = donations.aggregate(total=Sum('amount'))['total'] or 0
    
    # Apply sorting based on request parameters
    sort_by = request.GET.get('sort', 'newest')
    
    if sort_by == 'newest':
        donations = donations.order_by('-time')
    elif sort_by == 'oldest':
        donations = donations.order_by('time')
    elif sort_by == 'highest':
        donations = donations.order_by('-amount')
    elif sort_by == 'lowest':
        donations = donations.order_by('amount')
    
    # Calculate environmental impact estimates
    # (These are example calculations - adjust based on your actual metrics)
    estimated_trees = int(total_donations / 100)  # Example: 1 tree per ₹100
    estimated_co2 = estimated_trees * 20  # Example: 20kg CO2 per tree
    estimated_jobs = int(total_donations / 5000)  # Example: 1 job per ₹5000
    
    context = {
        'donations': donations,
        'total_donations': total_donations,
        'estimated_trees': estimated_trees,
        'estimated_co2': estimated_co2,
        'estimated_jobs': estimated_jobs,
        'sort_by': sort_by,
    }
    
    return render(request, 'dashboard/my-donations.html', context)

@login_required(login_url='login')
@phone_number_required
def my_transactions(request):
    # Get all payments for the current user
    payments = Payments.objects.filter(user=request.user)
    
    # Apply status filter if provided
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status__iexact=status_filter)
    
    # Calculate summary statistics
    total_amount = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    successful_payments = payments.filter(status__iexact='successful').count()
    
    # Order by most recent first
    payments = payments.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(payments, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'total_amount': total_amount,
        'successful_payments': successful_payments,
    }
    
    return render(request, 'dashboard/my-transactions.html', context)


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
