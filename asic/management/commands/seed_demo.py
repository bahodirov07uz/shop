"""Seed a small realistic demo catalog (idempotent via get_or_create).

Usage:
    python manage.py seed_demo
"""
import os

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from asic.models import (
    DeliveryInfo,
    DeliverySettings,
    Manufacturer,
    PageTitle,
    Product,
    ProductCategory,
    SiteSettings,
)


# Existing files on disk under MEDIA_ROOT/media/products/ (orphaned from
# previous DB, reused so gallery/images work without new uploads).
IMG = {
    "main": "media/products/20250611_105519.png",
    "img2": "media/products/20250611_105602.png",
    "img3": "media/products/20250611_105708.png",
    "alt1": "media/products/ICERIVER_KS5M-1.jpg",
    "alt2": "media/products/Goldshell_AL_BOX_360G_1.jpg",
    "alt3": "media/products/Whatsminer_M60_178_THs-1.jpg",
    "oq": "media/products/66b236099e39348f69673a65-Adobe-Stock-485047462-jpe-Photoroom.png",
}


def file_exists(path):
    from django.conf import settings

    return os.path.exists(os.path.join(settings.MEDIA_ROOT, path))


class Command(BaseCommand):
    help = "Create small realistic demo data (idempotent)"

    def handle(self, *args, **options):
        # --- base site rows so templates never crash on .first() = None ---
        SiteSettings.objects.get_or_create(
            id=1,
            defaults={
                "site_name": "SHOES.UZ",
                "email": "info@shoes.uz",
                "phone": "+998 71 200 00 00",
                "location": "Toshkent",
            },
        )
        DeliverySettings.objects.get_or_create(
            id=1,
            defaults={
                "air_delivery_rate": 25000,
                "air_delivery_name": "Kuryer (2-5 kun)",
                "sea_delivery_rate": 0,
                "sea_delivery_name": "Olib ketish (bepul)",
                "auto_delivery_rate": 50000,
                "auto_delivery_name": "Ekspress (1-2 kun)",
                "gtd_rb_cost": 0,
                "gtd_rb_name": "Kvitansiya",
                "dt_rf_cost": 0,
                "dt_rf_name": "Hisob-faktura",
                "is_active": True,
            },
        )
        DeliveryInfo.objects.get_or_create(
            id=1,
            defaults={
                "title": "Yetkazib berish haqida",
                "main_text": "Ertaga yetkazib beramiz. Topshirish punktiga yoki kuryer orqali.",
            },
        )
        PageTitle.objects.get_or_create(id=1)

        # --- manufacturers ---
        makers = {}
        for name, logo in [
            ("LABUTEN", "manufacturers/Bitmain.png"),
            ("Classic Step", "manufacturers/MicroBT.png"),
            ("Urban Walk", "manufacturers/Goldshell.png"),
        ]:
            m, _ = Manufacturer.objects.get_or_create(
                name=name,
                defaults={"logo": logo if file_exists(logo) else "manufacturers/Bitmain.png",
                          "is_active": True},
            )
            makers[name] = m

        # --- categories ---
        root, _ = ProductCategory.objects.get_or_create(
            name="Poyabzallar", defaults={"slug": "poyabzallar"})
        men, _ = ProductCategory.objects.get_or_create(
            name="Erkaklar poyabzali",
            defaults={"slug": "erkaklar-poyabzali", "parent": root},
        )
        kedalar, _ = ProductCategory.objects.get_or_create(
            name="Kedalar",
            defaults={"slug": "kedalar", "parent": men},
        )
        women, _ = ProductCategory.objects.get_or_create(
            name="Ayollar poyabzali",
            defaults={"slug": "ayollar-poyabzali", "parent": root},
        )

        products_spec = [
            {
                "name": "Erkaklar keda krossovkasi LABUTEN",
                "slug": "erkaklar-keda-krossovkasi-labuten",
                "manufacturer": "LABUTEN",
                "category": kedalar,
                "price": 109000,
                "old_price": 550000,
                "description": (
                    "Erkaklar uchun charm keda krossovkasi.\n"
                    "Kundalik yurish uchun qulay, yengil taglik.\n"
                    "O'lchamlar kichikroq chiqadi — 1 razmer katta oling."
                ),
                "specifications": "Material: charm\nTaglik: PVX\nMavsum: bahor-kuz",
                "is_featured": True,
                "colors": "Qora, Jigarrang, Oq",
                "sizes": "40, 41, 42, 43, 44",
                # (color, size) -> stock ; missing = default 5 ; 0 = out of stock (disabled demo)
                "stocks": {
                    ("Qora", "40"): 9, ("Qora", "41"): 7, ("Qora", "42"): 9,
                    ("Qora", "43"): 0, ("Qora", "44"): 4,
                    ("Jigarrang", "40"): 0, ("Jigarrang", "41"): 6,
                    ("Jigarrang", "42"): 2, ("Jigarrang", "43"): 3,
                    ("Jigarrang", "44"): 0,
                    ("Oq", "40"): 2, ("Oq", "41"): 0, ("Oq", "42"): 3,
                    ("Oq", "43"): 2, ("Oq", "44"): 5,
                },
                # (color, size) -> existing media file, so each color has its own images
                "variant_images": {
                    ("Qora", "42"): IMG["alt1"],
                    ("Qora", "41"): IMG["img2"],
                    ("Jigarrang", "41"): IMG["alt2"],
                    ("Jigarrang", "42"): IMG["alt3"],
                    ("Oq", "40"): IMG["oq"],
                    ("Oq", "42"): IMG["oq"],
                },
                "images": (IMG["main"], IMG["img2"], IMG["img3"]),
            },
            {
                "name": "Erkaklar klassik charm kedasi",
                "slug": "erkaklar-klassik-charm-kedasi",
                "manufacturer": "Classic Step",
                "category": kedalar,
                "price": 189000,
                "old_price": 259000,
                "description": "Ofis va kundalik uchun klassik charm keda.",
                "specifications": "Material: tabiiy charm",
                "is_featured": True,
                "colors": "Qora",
                "sizes": "41, 42, 43",
                "stocks": {("Qora", "41"): 5, ("Qora", "42"): 5, ("Qora", "43"): 5},
                "images": (IMG["alt1"], None, None),
            },
            {
                "name": "Ayollar sport krossovkasi",
                "slug": "ayollar-sport-krossovkasi",
                "manufacturer": "Urban Walk",
                "category": women,
                "price": 149000,
                "old_price": None,
                "description": "Yugurish va fitnes uchun yengil krossovka.",
                "specifications": "Material: tekstil",
                "is_featured": False,
                "colors": "Oq, Qora",
                "sizes": "37, 38, 39",
                "stocks": {("Oq", "37"): 2},  # rest default -> low-stock demo ("Only 2 left")
                "images": (IMG["alt2"], None, None),
            },
            {
                "name": "Bolalar kedasi (tugagan)",
                "slug": "bolalar-kedasi",
                "manufacturer": "Classic Step",
                "category": kedalar,
                "price": 99000,
                "old_price": None,
                "description": "Bolalar uchun mato keda. Hozircha zaxira tugagan.",
                "specifications": "Material: mato",
                "is_featured": False,
                "colors": "Ko'k",
                "sizes": "30, 31",
                "stocks": {("Ko'k", "30"): 0, ("Ko'k", "31"): 0},
                "images": (IMG["alt3"], None, None),
            },
            {
                "name": "Erkaklar bir variantli mokasini",
                "slug": "erkaklar-bir-variantli-mokasini",
                "manufacturer": "Classic Step",
                "category": kedalar,
                "price": 129000,
                "old_price": None,
                "description": "Bitta variantli klassik mokasini.",
                "specifications": "Material: charm",
                "is_featured": False,
                "colors": "Qora",
                "sizes": "42",
                "stocks": {("Qora", "42"): 4},
                "images": (IMG["alt1"], None, None),
            },
            {
                "name": "Ayollar sumkasi (variantsiz demo)",
                "slug": "ayollar-sumkasi-variantsiz-demo",
                "manufacturer": "Urban Walk",
                "category": women,
                "price": 59000,
                "old_price": None,
                "description": "Variantsiz demo mahsulot.",
                "specifications": "",
                "is_featured": False,
                "colors": "",
                "sizes": "",
                "stocks": {},
                "images": (IMG["alt2"], None, None),
            },
        ]

        for spec in products_spec:
            img_main, img2, img3 = spec["images"]
            defaults = {
                "name": spec["name"],
                "manufacturer": makers[spec["manufacturer"]],
                "category": spec["category"],
                "price": spec["price"],
                "old_price": spec["old_price"],
                "description": spec["description"],
                "specifications": spec["specifications"],
                "is_featured": spec["is_featured"],
                "is_active": True,
                "variant_colors": spec["colors"],
                "variant_sizes": spec["sizes"],
                "default_variant_stock": 5,
            }
            # only set image fields when file really exists on disk
            if img_main and file_exists(img_main):
                defaults["images"] = img_main
            if img2 and file_exists(img2):
                defaults["image2"] = img2
            if img3 and file_exists(img3):
                defaults["image3"] = img3

            product, created = Product.objects.get_or_create(
                slug=spec["slug"], defaults=defaults)
            if not created:
                # keep demo deterministic: refresh core fields, keep variants
                for k, v in defaults.items():
                    setattr(product, k, v)
                product.save()

            # deterministic per-variant stock (generate_variants ran inside save())
            variant_images = spec.get("variant_images", {})
            for variant in product.variants.all():
                key = (variant.color, variant.size)
                changed = False
                if key in spec["stocks"]:
                    stock = spec["stocks"][key]
                    if variant.stock != stock or not variant.is_active:
                        variant.stock = stock
                        variant.is_active = True
                        changed = True
                if key in variant_images and file_exists(variant_images[key]):
                    current = variant.image.name if variant.image else ""
                    if current != variant_images[key]:
                        variant.image = variant_images[key]
                        changed = True
                if changed:
                    variant.save()
            product.update_total_stock()
            product.refresh_from_db()
            self.stdout.write(
                f"{'created' if created else 'updated'}: {product.slug} "
                f"stock={product.stock} variants={product.variants.filter(is_active=True).count()}"
            )

        self.stdout.write(self.style.SUCCESS("seed_demo done (idempotent)."))
