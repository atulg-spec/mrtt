from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserForm
from .models import CustomUser
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from accounts.utils import phone_number_required
from .forms import PhoneNumberForm, KYCVerificationForm
from django.contrib.auth.forms import SetPasswordForm

def google_login_redirect(request):
    ref = request.GET.get('ref')

    if not ref:
        try:
            # Get any active superuser's referral code as fallback
            superuser = CustomUser.objects.filter(is_superuser=True, referral_code__isnull=False).first()
            if superuser:
                ref = superuser.referral_code
        except CustomUser.DoesNotExist:
            pass

    if ref:
        request.session['ref_code'] = ref

    return redirect('social:begin', backend='google-oauth2')


@login_required
def phone_number_registration(request):
    user = request.user

    # If user already has phone number, redirect
    if user.phone_number:
        if not user.aadhaar_number or not user.date_of_birth:
            return redirect('/accounts/kyc-verification/')
        else:
            return redirect('/dashboard/')

    if request.method == 'POST':
        form = PhoneNumberForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('/accounts/kyc-verification/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('/accounts/phone-number-registration/')
    else:
        form = PhoneNumberForm(instance=user)

    return render(request, 'accounts/phone_number_registration.html', {'form': form})



@login_required
def kyc_verification(request):
    if not request.user.phone_number:
        return redirect('/accounts/phone-number-registration/')

    if request.method == 'POST':
        form = KYCVerificationForm(request.POST)
        if form.is_valid():
            request.user.aadhaar_number = form.cleaned_data['aadhaar_number']
            request.user.date_of_birth = form.cleaned_data['date_of_birth']
            request.user.pan_number = form.cleaned_data['pan_number']
            request.user.save()
            return redirect('/dashboard/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        if request.user.aadhaar_number:
            return redirect('/dashboard/')
        form = KYCVerificationForm()
    return render(request, 'accounts/kyc_verification.html', {'form': form})


@login_required(login_url = 'login')
@phone_number_required
def set_password_view(request):
    if request.method == "POST":
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been set successfully ✅")
            return redirect("/dashboard/")
    else:
        form = SetPasswordForm(request.user)
    return render(request, "accounts/set-password.html", {"form": form})


def login(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    return render(request, 'accounts/login-signup.html')


@login_required(login_url = 'login')
@phone_number_required
def logout(request):
    auth.logout(request)
    messages.success(request, "You have successfully logged out. See you again soon!")
    return redirect('login')
