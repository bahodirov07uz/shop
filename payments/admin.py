from django.contrib import admin

# Register your models here.
# payments/admin.py
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'billing_id', 'amount', 'currency', 'status']
    readonly_fields = ['created_at', 'status']
