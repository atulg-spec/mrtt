from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path("invitations/", views.invitations_view, name="invitations"),
    path("invitations/<int:user_id>/", views.invitations_view, name="invitations_detail"),


    path('my-invites/', views.my_invites, name='my_invites'),
    path('my-account/', views.my_account, name='my_account'),
    path('my-donations/', views.my_donations, name='my_donations'),
    path('my-transactions/', views.my_transactions, name='my_transactions'),
    path('apply/', views.apply_job, name='apply_job'),
    path('selfie-with-tree/', views.selfie_with_tree, name='selfie_with_tree'),
]
