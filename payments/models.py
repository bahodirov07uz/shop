from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Payment(models.Model):
    STATUS_CHOICES = (('pending','Pending'),('success','Success'),('failed','Failed'))
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    billing_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    invoice_uuid = models.CharField(max_length=100, blank=True, null=True)
    invoice_link = models.URLField(blank=True, null=True)
    temp_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

