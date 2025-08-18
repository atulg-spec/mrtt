from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('phone-number-registration/', views.phone_number_registration, name='phone_number_registration'),
    path('kyc-verification/', views.kyc_verification, name='kyc_verification'),
    path('login/', views.login, name='login'),

    path("password/set/", views.set_password_view, name="set_password"),
    # path("password/set/done/", views.set_password_done, name="password_set_done"),

    path('logout/', views.logout, name='logout'),
]
