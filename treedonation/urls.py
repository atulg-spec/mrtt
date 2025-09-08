from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from accounts.views import google_login_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('social-auth/', include('social_django.urls',namespace='social')),
    path('login/', google_login_redirect, name='google_login_redirect'),
    path('accounts/', include('accounts.urls')),
    path('donate/', include('donation.urls')),
    path('', include('home.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('earnings/', include('earning.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]