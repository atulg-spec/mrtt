from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('my-donations/', views.my_donations, name='my_donations'),
    path('my-transactions/', views.my_transactions, name='my_transactions'),
    path('apply/', views.apply_job, name='apply_job'),
]
