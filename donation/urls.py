from django.urls import path
from . import views

urlpatterns = [
    path('', views.donate, name='donate'),
    # Registration Payment Setup
    path('complete-registration/', views.complete_registration, name='complete_registration'),
    path('register/proceed-payment/', views.registration_proceed_payment, name='proceed_payment'),
    path('register/razorpay/success/', views.registration_razorpay_success, name='razorpay_success'),
    path('register/razorpay/failure/', views.registration_razorpay_failure, name='razorpay_failure'),

    # Donation Payment Setup
    path('proceed-payment/', views.proceed_payment, name='proceed_payment'),
    path('upicallback/<str:orderId>/', views.upicallback, name='upicallback'),
    path('razorpay/success/', views.razorpay_success, name='razorpay_success'),
    path('razorpay/failure/', views.razorpay_failure, name='razorpay_failure'),

    # Manual Payment Urls
    path('proceed-manual-payments/', views.proceed_manual_payment, name='proceed_manual_payment'),
]
