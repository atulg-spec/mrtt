from django.urls import path
from . import views

urlpatterns = [
    path('', views.earning_dashboard, name='earning-dashboard'),
]
