from django.core.exceptions import PermissionDenied
from .models import CustomUser

def require_referral_code(strategy, backend, request, *args, **kwargs):
    if kwargs.get('user'):  # User already exists
        return

    ref_code = strategy.session_get('ref_code')
    if not ref_code:
        raise PermissionDenied("Referral code required to register.")

    try:
        referrer = CustomUser.objects.get(referral_code=ref_code)
        strategy.session_set('referrer_id', referrer.id)
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Invalid referral code.")

def set_referral_relationship(strategy, backend, user, *args, **kwargs):
    referrer_id = strategy.session_get('referrer_id')
    if referrer_id and not user.referred_by:
        try:
            referrer = CustomUser.objects.get(id=referrer_id)
            user.referred_by = referrer
            user.save()
        except CustomUser.DoesNotExist:
            pass
