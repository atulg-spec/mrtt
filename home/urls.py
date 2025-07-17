# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('services/', views.services, name='services'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('contactus/', views.contactus, name='contactus'),
    path('careers/', views.careers, name='careers'),
    path('news/', views.news, name='news'),
]