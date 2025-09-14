from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.utils import phone_number_required
from .models import UserLevelReward, Wallet
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Wallet, WithdrawalRequest, WithdrawalMethod, UserBankAccount, UserUPIAccount
from .forms import WithdrawalForm, BankAccountForm, UPIAccountForm


# Create your views here.
@login_required(login_url = 'login')
@phone_number_required
def earning_dashboard(request):
    user = request.user

    if not user.registration_fee_paid:
        return redirect('/donate/complete-registration/')
    
    if not request.user.has_usable_password():
        return redirect("set_password")
    
    wallet = Wallet.objects.get(user=user)
    
    # Get user's level rewards
    level_rewards = UserLevelReward.objects.filter(user=user).order_by('-level')
    
    # Calculate total earnings
    total_earnings = wallet.balance + wallet.locked_balance
    
    context = {
        'wallet': wallet,
        'level_rewards': level_rewards,
        'total_earnings': total_earnings,
    }
    
    return render(request, 'earning/dashboard.html', context)


@login_required(login_url='login')
@phone_number_required
def withdraw_funds(request):
    user = request.user
    
    if not user.registration_fee_paid:
        return redirect('/donate/complete-registration/')
    
    if not request.user.has_usable_password():
        return redirect("set_password")
    
    # Get user's wallet
    wallet = Wallet.objects.get(user=user)
    
    # Get active withdrawal methods
    withdrawal_methods = WithdrawalMethod.objects.filter(is_active=True)
    
    # Get user's saved accounts
    bank_accounts = UserBankAccount.objects.filter(user=user)
    upi_accounts = UserUPIAccount.objects.filter(user=user)
    
    # Withdrawal history
    withdrawal_history = WithdrawalRequest.objects.filter(user=user).order_by('-created_at')[:5]
    
    if request.method == 'POST':
        form = WithdrawalForm(request.POST, user=user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create withdrawal request
                    withdrawal = form.save(commit=False)
                    withdrawal.user = user
                    
                    # Check if user has sufficient balance
                    if withdrawal.amount > wallet.balance:
                        messages.error(request, 'Insufficient balance for this withdrawal.')
                        return redirect('withdraw_funds')
                    
                    # Check if amount meets minimum requirement for selected method
                    try:
                        method = WithdrawalMethod.objects.get(code=withdrawal.method)
                        if withdrawal.amount < method.min_amount:
                            messages.error(request, f'Minimum withdrawal amount for {method.name} is ₹{method.min_amount}.')
                            return redirect('withdraw_funds')
                    except WithdrawalMethod.DoesNotExist:
                        messages.error(request, 'Selected withdrawal method is not available.')
                        return redirect('withdraw_funds')
                    
                    withdrawal.save()
                                        
                    messages.success(request, f'Withdrawal request for ₹{withdrawal.amount} submitted successfully!')
                    return redirect('withdrawal_history')
                    
            except Exception as e:
                messages.error(request, f'Error processing withdrawal: {str(e)}')
    else:
        form = WithdrawalForm(user=user)
    
    context = {
        'wallet': wallet,
        'withdrawal_methods': withdrawal_methods,
        'bank_accounts': bank_accounts,
        'upi_accounts': upi_accounts,
        'withdrawal_history': withdrawal_history,
        'form': form,
    }
    
    return render(request, 'earning/withdraw.html', context)


@login_required(login_url='login')
@require_POST
def add_bank_account(request):
    form = BankAccountForm(request.POST)
    if form.is_valid():
        bank_account = form.save(commit=False)
        bank_account.user = request.user
        
        # If this is the first account, set as primary
        if not UserBankAccount.objects.filter(user=request.user).exists():
            bank_account.is_primary = True
            
        bank_account.save()
        messages.success(request, 'Bank account added successfully!')
    else:
        messages.error(request, 'Error adding bank account. Please check the details.')
    
    return redirect('withdraw_funds')


@login_required(login_url='login')
@require_POST
def add_upi_account(request):
    form = UPIAccountForm(request.POST)
    if form.is_valid():
        upi_account = form.save(commit=False)
        upi_account.user = request.user
        
        # If this is the first account, set as primary
        if not UserUPIAccount.objects.filter(user=request.user).exists():
            upi_account.is_primary = True
            
        upi_account.save()
        messages.success(request, 'UPI account added successfully!')
    else:
        messages.error(request, 'Error adding UPI account. Please check the details.')
    
    return redirect('withdraw_funds')


@login_required(login_url='login')
def withdrawal_history(request):
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'withdrawals': withdrawals,
    }
    
    return render(request, 'earning/withdrawal_history.html', context)


@login_required(login_url='login')
@require_POST
def set_primary_account(request):
    account_type = request.POST.get('account_type')
    account_id = request.POST.get('account_id')
    
    try:
        if account_type == 'bank':
            # Set all bank accounts to non-primary
            UserBankAccount.objects.filter(user=request.user).update(is_primary=False)
            # Set selected account as primary
            bank_account = UserBankAccount.objects.get(id=account_id, user=request.user)
            bank_account.is_primary = True
            bank_account.save()
            
        elif account_type == 'upi':
            # Set all UPI accounts to non-primary
            UserUPIAccount.objects.filter(user=request.user).update(is_primary=False)
            # Set selected account as primary
            upi_account = UserUPIAccount.objects.get(id=account_id, user=request.user)
            upi_account.is_primary = True
            upi_account.save()
            
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required(login_url='login')
@csrf_exempt
@require_POST
def delete_account(request):
    account_type = request.POST.get('account_type')
    account_id = request.POST.get('account_id')
    
    try:
        if account_type == 'bank':
            account = UserBankAccount.objects.get(id=account_id, user=request.user)
            account.delete()
            
        elif account_type == 'upi':
            account = UserUPIAccount.objects.get(id=account_id, user=request.user)
            account.delete()
            
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})