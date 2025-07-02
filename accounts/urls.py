from django.urls import path
from . import views


urlpatterns = [
    path('phone-number-registration/', views.phone_number_registration, name='phone_number_registration'),
    path('kyc-verification/', views.kyc_verification, name='kyc_verification'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
