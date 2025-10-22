from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'payments'

urlpatterns = [
    path('success', views.payment_success, name='payment_success'),
    path('failed', views.payment_failed, name='payment_fail'),
]
