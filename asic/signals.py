# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Profile
from django.core.mail import send_mail

from django.conf import settings

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


@receiver(user_signed_up)
def save_name_to_profile(request, user, **kwargs):
    socialaccount = user.socialaccount_set.filter(provider='google').first()
    if socialaccount:
        data = socialaccount.extra_data
        first_name = data.get('given_name', '')
        last_name = data.get('family_name', '')
        
        # Profile yaratilmagan bo‘lsa yaratamiz yoki mavjudini olamiz
        profile, created = Profile.objects.get_or_create(user=user)
        profile.first_name = first_name
        profile.last_name = last_name
        profile.save()


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject="Xush kelibsiz!",
            message=f"Здравствуйте {instance.username}, добро пожаловать на china-asic.com!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )