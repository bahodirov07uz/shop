from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Payment(models.Model):
    STATUS_CHOICES = (
        ('в обработке', 'В обработке'),
        ('успешно', 'Успешно'), 
        ('ошибка', 'Ошибка')
    )
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    billing_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='в обработке')  # uzunligi 15 ga oshirildi
    invoice_uuid = models.CharField(max_length=100, blank=True, null=True)
    invoice_link = models.URLField(blank=True, null=True)
    session_key = models.CharField(max_length=255, blank=True, null=True)
    temp_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
