"""anonymous URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from __future__ import absolute_import

import os

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
                  path(os.environ.get('ADMIN_URL', "admin/"), admin.site.urls),

                  path('reset/',
                       auth_views.PasswordResetView.as_view(
                           template_name='registration/password_reset.html',
                           email_template_name='registration/password_reset_email.html',
                           subject_template_name='registration/password_reset_subject.txt'
                       ),
                       name='password_reset'),
                  path('reset/done/',
                       auth_views.PasswordResetDoneView.as_view(
                           template_name='registration/password_reset_done.html'),
                       name='password_reset_done'
                       ),
                  path('reset/<uidb64>/<token>/',
                       auth_views.PasswordResetConfirmView.as_view(
                           template_name='registration/password_reset_confirm.html'),
                       name='password_reset_confirm'),
                  path('reset/complete/',
                       auth_views.PasswordResetCompleteView.as_view(
                           template_name='registration/password_reset_complete.html'),
                       name='password_reset_complete'),

                  path('api/', include('anon_api.urls')),

                  path('', include('anon.urls')),

              ]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
