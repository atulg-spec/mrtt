from django.urls import path
from . import views

urlpatterns = [
    path('', views.earning_dashboard, name='earning-dashboard'),
    path('withdraw/', views.withdraw_funds, name='withdraw_funds'),
    path('withdrawal/history/', views.withdrawal_history, name='withdrawal_history'),
    path('withdraw/add-bank-account/', views.add_bank_account, name='add_bank_account'),
    path('withdraw/add-upi-account/', views.add_upi_account, name='add_upi_account'),
    path('withdraw/set-primary-account/', views.set_primary_account, name='set_primary_account'),
    path('withdraw/delete-account/', views.delete_account, name='delete_account'),
]
