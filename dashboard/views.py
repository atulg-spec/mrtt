from django.shortcuts import render, get_object_or_404, redirect
from management.models import JobOpening
from .forms import JobApplicationForm
from django.contrib.auth.decorators import login_required
from accounts.utils import phone_number_required
from accounts.models import CustomUser
from django.core.paginator import Paginator  # Add this import
from donation.models import Donation, Payments, Registration_fee
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

    if not user.registration_fee_paid:
        return redirect('/donate/complete-registration/')
    
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



@login_required(login_url = 'login')
@phone_number_required
def my_invites(request):
    user = request.user

    if not user.registration_fee_paid:
        return redirect('/donate/complete-registration/')
    
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
        'referrals': referrals,
    }
    
    return render(request, 'dashboard/my-invites.html', context)




@login_required(login_url='login')
@phone_number_required
def my_donations(request):
    # Get all donations and registration fees for the current user
    donations = Donation.objects.filter(user=request.user)
    registration_fees = Registration_fee.objects.filter(user=request.user)
    
    # Combine both querysets into a single list of transactions
    transactions = []
    
    for fee in registration_fees:
        transactions.append({
            'type': 'Registration Fee',
            'amount': fee.amount,
            'time': fee.time,
            'is_registration': True
        })
    
    for donation in donations:
        transactions.append({
            'type': 'Donation',
            'amount': donation.amount,
            'time': donation.time,
            'is_registration': False
        })
    
    # Sort transactions by time (newest first)
    transactions.sort(key=lambda x: x['time'], reverse=True)
    
    # Calculate summary statistics
    total_donations = donations.aggregate(total=Sum('amount'))['total'] or 0
    total_registration = registration_fees.aggregate(total=Sum('amount'))['total'] or 0
    total_contributed = total_donations + total_registration
    
    # Pagination
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'total_donations': total_donations,
        'total_registration': total_registration,
        'total_contributed': total_contributed,
        'donations_count': donations.count(),
        'registration_count': registration_fees.count(),
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
    total_amount = payments.filter(status='Successful').aggregate(total=Sum('amount_paid'))['total'] or 0
    successful_payments = payments.filter(status__iexact='successful').count()
    
    # Order by most recent first
    payments = payments.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(payments, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'payments_count': payments.count,
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


@login_required(login_url = 'login')
@phone_number_required
def my_account(request):
    return render(request, 'dashboard/my-account.html')
