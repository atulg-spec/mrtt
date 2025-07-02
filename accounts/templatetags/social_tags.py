# myapp/templatetags/social_tags.py
from django import template
from social_django.models import UserSocialAuth

register = template.Library()

@register.filter
def google_profile_picture(user):
    try:
        google_account = UserSocialAuth.objects.get(user=user, provider='google-oauth2')
        return google_account.extra_data.get('picture')
    except UserSocialAuth.DoesNotExist:
        return None