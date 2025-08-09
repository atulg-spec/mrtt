from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserForm
from .models import CustomUser
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from accounts.utils import phone_number_required
from .forms import PhoneNumberForm, KYCVerificationForm

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
            for e in form.errors:
                messages.error(request,e)
            return redirect('/')
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
            try:
                request.user.pan_number = form.cleaned_data['pan_number']
            except:
                pass
            request.user.save()
            return redirect('/dashboard/')
    else:
        if request.user.aadhaar_number:
            return redirect('/dashboard/')
        form = KYCVerificationForm()
    return render(request, 'accounts/kyc_verification.html', {'form': form})


def login(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    return render(request, 'accounts/login-signup.html')


@login_required(login_url = 'login')
@phone_number_required
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')
