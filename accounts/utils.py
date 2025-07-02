from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps
from social_django.models import UserSocialAuth

# Custom decorator to check for phone number
def phone_number_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.phone_number:
                return redirect('phone_number_registration')
            
            if not request.user.aadhaar_number or not request.user.date_of_birth or not request.user.pan_number:
                print('redirecting')
                return redirect('kyc_verification')

            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied  # If user is not authenticated, deny access
    return _wrapped_view


def get_google_profile_pic(user):
    try:
        social_account = user.social_auth.get(provider='google-oauth2')
        return social_account.extra_data.get('picture', None)
    except UserSocialAuth.DoesNotExist:
        return None
