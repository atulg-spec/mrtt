from django.urls import path
from . import views

urlpatterns = [
    path('', views.donate, name='donate'),
    path('proceed-payment/', views.proceed_payment, name='proceed_payment'),
    path('razorpay/success/', views.razorpay_success, name='razorpay_success'),
    path('razorpay/failure/', views.razorpay_failure, name='razorpay_failure'),
]
