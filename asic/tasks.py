import requests
from django.core.files.base import ContentFile
from celery import shared_task
from asic.models import Product
from urllib.parse import urlparse
import os

def download_and_save_image(instance, url_field, image_field):
    url = getattr(instance, url_field)
    if not url:
        return
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        filename = os.path.basename(urlparse(url).path) or f"{instance.slug}.jpg"
        content = ContentFile(response.content)
        getattr(instance, image_field).save(filename, content, save=True)
        print(f"✅ Rasm yuklandi: {instance.name} ({url})")
    except Exception as e:
        print(f"❌ Xato yuklashda: {instance.name} | {e}")

@shared_task
def download_product_images():
    for p in Product.objects.all():
        if not p.images and p.image_url:
            download_and_save_image(p, 'image_url', 'images')
        if not p.image2 and p.image2_url:
            download_and_save_image(p, 'image2_url', 'image2')
        if not p.image3 and p.image3_url:
            download_and_save_image(p, 'image3_url', 'image3')
