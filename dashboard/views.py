from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import JobApplicationForm
from django.contrib.auth.decorators import login_required
from accounts.utils import phone_number_required
from accounts.models import CustomUser
from django.core.paginator import Paginator  # Add this import
from donation.models import Donation, Payments, Registration_fee, ManualPayment
from django.db.models import Sum
from accounts.forms import UserProfileForm

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
    
    if not request.user.has_usable_password():
        return redirect("set_password")
    
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
    # Get all transactions for the current user
    payments = Payments.objects.filter(user=request.user)
    manual_payments = ManualPayment.objects.filter(user=request.user,status='PENDING')
    
    # Get status filter from request
    status_filter = request.GET.get('status')
    
    # Combine both querysets with consistent structure
    all_transactions = []
    
    # Process regular payments
    for payment in payments:
        all_transactions.append({
            'id': payment.razorpay_payment_id,
            'type': 'Payment',
            'payment_method': payment.payment_method,
            'amount': float(payment.amount_paid),
            'status': payment.status,
            'date': payment.created_at,
            'is_manual': False,
            'transaction_id': payment.razorpay_payment_id if payment.payment_method != 'manual' else payment.manual_transaction_id,
            'screenshot': None
        })
    
    # Process manual payments (convert status to match regular payments)
    for manual_payment in manual_payments:
        status_map = {
            'PENDING': 'Pending',
            'VERIFIED': 'Successful',
            'REJECTED': 'Failed'
        }
        all_transactions.append({
            'id': manual_payment.transaction_id,
            'type': 'Manual Payment',
            'payment_method': 'manual',
            'amount': manual_payment.amount,
            'status': status_map.get(manual_payment.status, manual_payment.status),
            'date': manual_payment.created_at,
            'is_manual': True,
            'transaction_id': manual_payment.transaction_id,
            'screenshot': manual_payment.screenshot.url if manual_payment.screenshot else None
        })
    
    # Apply status filter if provided
    if status_filter:
        status_filter = status_filter.lower()
        if status_filter == 'pending':
            all_transactions = [t for t in all_transactions if t['status'].lower() == 'pending']
        elif status_filter == 'successful':
            all_transactions = [t for t in all_transactions if t['status'].lower() == 'successful']
        elif status_filter == 'failed':
            all_transactions = [t for t in all_transactions if t['status'].lower() == 'failed']
    
    # Sort all transactions by date (newest first)
    all_transactions.sort(key=lambda x: x['date'], reverse=True)
    
    # Calculate summary statistics
    total_amount = sum(
        float(t['amount']) for t in all_transactions 
        if t['status'].lower() == 'successful'
    )
    successful_payments = sum(
        1 for t in all_transactions 
        if t['status'].lower() == 'successful'
    )
    pending_payments = sum(
        1 for t in all_transactions 
        if t['status'].lower() == 'pending'
    )
    
    # Pagination
    paginator = Paginator(all_transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'payments_count': len(all_transactions),
        'total_amount': total_amount,
        'successful_payments': successful_payments,
        'pending_payments': pending_payments,
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
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('my_account')  # Replace with your URL name
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'dashboard/my-account.html', {'form': form})