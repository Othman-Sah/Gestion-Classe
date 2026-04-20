"""
URL configuration for gestion_presence project.

The `urlpatterns` list routes URLs to view. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from appel.views import root_language_redirect

# Non-prefixed URLs (available in all languages)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', root_language_redirect, name='root_redirect'),
    path('login/', root_language_redirect, name='login_redirect'),
]

# Language-prefixed URLs  
urlpatterns += i18n_patterns(
    path('', include('appel.urls')),
    prefix_default_language=True,
)
