from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('my-invites/', views.my_invites, name='my_invites'),
    path('my-account/', views.my_account, name='my_account'),
    path('my-donations/', views.my_donations, name='my_donations'),
    path('my-transactions/', views.my_transactions, name='my_transactions'),
    path('apply/', views.apply_job, name='apply_job'),
]
