from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('update-user-location/', views.UpdateUserLocationView.as_view(), name='update_user_location'),
    path('phone-number-registration/', views.phone_number_registration, name='phone_number_registration'),
    path('kyc-verification/', views.kyc_verification, name='kyc_verification'),
    path('login/', views.login, name='login'),
    path("password/set/", views.set_password_view, name="set_password"),
    # path("password/set/done/", views.set_password_done, name="password_set_done"),
    path('logout/', views.logout, name='logout'),

    # Forgot Password
    path('password_reset/',
     auth_views.PasswordResetView.as_view(
         template_name='registration/password_reset_form.html',
         email_template_name='registration/password_reset_custom_email.html',
         subject_template_name='registration/password_reset_subject.txt',
         success_url='/accounts/password_reset/done/'
     ),
    name='password_reset'),

    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),

    # step 3: link in email goes to this view with uidb64 and token
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),

    # step 4: password successfully changed
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),

]
