from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Sum
from ckeditor.fields import RichTextField

from .utils import calculate_product_discount, get_product_discounts


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Brend nomi")
    logo = models.ImageField(upload_to="manufacturers/", verbose_name="Logo")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Brend"
        verbose_name_plural = "Brendlar"

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    name = models.CharField(max_length=200, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Ism")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Familiya")
    father_name = models.CharField(max_length=150, blank=True, verbose_name="Sharif")
    address_street = models.CharField(max_length=255, blank=True, null=True, verbose_name="Kocha")
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name="Mamlakat")
    home = models.CharField(max_length=100, null=True, blank=True, verbose_name="Uy")
    address_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Shahar")
    address_region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Viloyat")
    address_postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Pochta indeksi")

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profillar"

    def __str__(self):
        return f"Profil: {self.user.username}"


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    image = models.ImageField(
        upload_to="categories/",
        null=True,
        blank=True,
        verbose_name="Kategoriya rasmi",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=" kategoriya",
    )

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="O'lcham")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "O'lcham"
        verbose_name_plural = "O'lchamlar"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE, verbose_name="Brend"
    )
    category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL, null=True, verbose_name="Kategoriya"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Narx",
    )
    old_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        verbose_name="Eski narx",
    )
    description = models.TextField(verbose_name="Tavsif")
    specifications = models.TextField(blank=True, verbose_name="Xususiyatlar")
    images = models.ImageField(
        upload_to="media/products",
        null=True,
        blank=True,
        verbose_name="Asosiy rasm",
    )
    image2 = models.ImageField(
        upload_to="media/products",
        null=True,
        blank=True,
        verbose_name="Qo'shimcha rasm 1",
    )
    image3 = models.ImageField(
        upload_to="media/products",
        null=True,
        blank=True,
        verbose_name="Qo'shimcha rasm 2",
    )
    is_featured = models.BooleanField(default=False, verbose_name="Tavsiya etiladi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Yaratilgan sana"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

    variant_colors = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ranglar (vergul bilan)",
        help_text="Masalan: black, brown, white",
    )
    variant_sizes = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="O'lchamlar (vergul bilan)",
        help_text="Masalan: 40, 41, 42",
    )
    sizes = models.ManyToManyField(
        Size, blank=True, related_name="products", verbose_name="O'lchamlar (tanlab)"
    )
    default_variant_stock = models.PositiveIntegerField(
        default=0, verbose_name="Variant uchun boshlangich zaxira"
    )

    stock = models.PositiveIntegerField(
        default=0, editable=False, verbose_name="Jami zaxira"
    )

    meta_title = models.CharField(
        max_length=255, blank=True, verbose_name="SEO title"
    )
    meta_description = models.CharField(
        max_length=255, blank=True, verbose_name="SEO description"
    )

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["-created_at"]

    @property
    def current_price(self):
        discount_info = calculate_product_discount(self, self.price)
        return discount_info["discounted_price"]

    def get_discount_info(self):
        return calculate_product_discount(self, self.price)

    def has_discount(self):
        return bool(get_product_discounts(self))

    def total_stock(self):
        return self.stock

    def parsed_colors(self):
        return [c.strip() for c in self.variant_colors.split(",") if c.strip()]

    def parsed_sizes(self):
        if self.sizes.exists():
            return [s.name for s in self.sizes.all()]
        return [s.strip() for s in self.variant_sizes.split(",") if s.strip()]

    def _ensure_slug(self):
        if self.slug:
            return
        base_slug = slugify(self.name) or "product"
        slug = base_slug
        i = 1
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{i}"
            i += 1
        self.slug = slug

    def generate_variants(self):
        colors = self.parsed_colors()
        sizes = self.parsed_sizes()
        if not colors or not sizes:
            return

        if not self.sizes.exists() and sizes:
            size_objects = []
            for size_name in sizes:
                size_obj, _ = Size.objects.get_or_create(name=size_name)
                size_objects.append(size_obj)
            if size_objects:
                self.sizes.set(size_objects)

        existing = {
            (v.color.lower(), v.size.lower()): v for v in self.variants.all()
        }
        desired = set()

        for color in colors:
            for size in sizes:
                key = (color.lower(), size.lower())
                desired.add(key)
                sku = f"{self.slug}-{slugify(color)}-{slugify(size)}"

                variant = existing.get(key)
                if variant:
                    updates = []
                    if variant.sku != sku:
                        variant.sku = sku
                        updates.append("sku")
                    if not variant.is_active:
                        variant.is_active = True
                        updates.append("is_active")
                    if updates:
                        variant.save(update_fields=updates)
                else:
                    ProductVariant.objects.create(
                        product=self,
                        color=color,
                        size=size,
                        sku=sku,
                        stock=self.default_variant_stock,
                        is_active=True,
                    )

        for key, variant in existing.items():
            if key not in desired and variant.is_active:
                variant.is_active = False
                variant.save(update_fields=["is_active"])

        self.update_total_stock()

    def update_total_stock(self):
        total = (
            self.variants.filter(is_active=True).aggregate(total=Sum("stock"))["total"]
            or 0
        )
        Product.objects.filter(pk=self.pk).update(stock=total)

    def save(self, *args, **kwargs):
        self._ensure_slug()
        super().save(*args, **kwargs)
        self.generate_variants()

    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    image = models.ImageField(
        upload_to="variants/",
        null=True,
        blank=True,
        verbose_name="Variant rasmi",
    )
    color = models.CharField(max_length=50, verbose_name="Rang")
    size = models.CharField(max_length=20, verbose_name="O'lcham")
    sku = models.CharField(max_length=120, unique=True, verbose_name="SKU")
    stock = models.PositiveIntegerField(default=0, verbose_name="Zaxira")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Variant"
        verbose_name_plural = "Variantlar"
        unique_together = ("product", "color", "size")
        ordering = ["color", "size"]

    def save(self, *args, **kwargs):
        if not self.sku:
            base = self.product.slug
            self.sku = f"{base}-{slugify(self.color)}-{slugify(self.size)}"
        super().save(*args, **kwargs)
        self.product.update_total_stock()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.update_total_stock()

    def __str__(self):
        return self.sku


class Order(models.Model):
    DELIVERY_TYPES = [
        ("courier", "Kuryer"),
        ("pickup", "Olib ketish"),
        ("express", "Ekspress"),
    ]

    DOCUMENT_TYPES = [
        ("receipt", "Kvitansiya"),
        ("invoice", "Hisob-faktura"),
    ]

    STATUS_CHOICES = [
        ("new", "Yangi buyurtma"),
        ("processing", "Jarayonda"),
        ("shipped", "Yuborildi"),
        ("customs", "Bojxonada"),
        ("sorting", "Saralash markazida"),
        ("delivering", "Yetkazilmoqda"),
        ("pickup_ready", "Olib ketishga tayyor"),
        ("completed", "Yakunlandi"),
        ("cancelled", "Bekor qilindi"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", verbose_name="Foydalanuvchi"
    )
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Buyurtma raqami")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Holat"
    )
    delivery_type = models.CharField(
        max_length=10, choices=DELIVERY_TYPES, verbose_name="Yetkazib berish turi"
    )
    delivery_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Yetkazib berish narxi"
    )
    document_type = models.CharField(
        max_length=10, choices=DOCUMENT_TYPES, verbose_name="Hujjat turi"
    )
    document_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Hujjat narxi"
    )
    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Oraliq summa"
    )
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, verbose_name="Chegirma foizi"
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Chegirma summasi"
    )
    total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Jami summa"
    )
    payment_id = models.CharField(max_length=100, blank=True, verbose_name="To'lov ID")
    payment_status = models.CharField(
        max_length=20, default="pending", verbose_name="To'lov holati"
    )
    shipping_address = models.TextField(verbose_name="Yetkazib berish manzili")
    billing_address = models.TextField(blank=True, verbose_name="To'lov manzili")
    notes = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    last_status_update = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, verbose_name="Holat yangilangan sana"
    )

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Buyurtma #{self.order_number} - {self.user.username}"

    def get_dynamic_delivery_name(self):
        settings = DeliverySettings.objects.filter(is_active=True).first()
        if not settings:
            return self.get_delivery_type_display()

        if self.delivery_type == "courier":
            return settings.air_delivery_name
        if self.delivery_type == "pickup":
            return settings.sea_delivery_name
        if self.delivery_type == "express":
            return settings.auto_delivery_name
        return self.get_delivery_type_display()

    def get_dynamic_document_name(self):
        settings = DeliverySettings.objects.filter(is_active=True).first()
        if not settings:
            return self.get_document_type_display()

        if self.document_type == "receipt":
            return settings.gtd_rb_name
        if self.document_type == "invoice":
            return settings.dt_rf_name
        return self.get_document_type_display()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            from .models import OrderStatusRule

            rules = OrderStatusRule.objects.filter(
                is_active=True, immediate=True
            ).order_by("order_priority")

            for rule in rules:
                if self.status != rule.status:
                    self.status = rule.status
                    self.last_status_update = timezone.now()
                    super().save(update_fields=["status", "last_status_update"])
                    break


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE, verbose_name="Buyurtma"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Mahsulot")
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Variant",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narx")
    quantity = models.PositiveIntegerField(verbose_name="Miqdor")
    original_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Asl narx"
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Chegirma summasi"
    )

    class Meta:
        verbose_name = "Buyurtma pozitsiyasi"
        verbose_name_plural = "Buyurtma pozitsiyalari"

    def get_cost(self):
        return self.quantity * self.price

    def __str__(self):
        variant_label = f" ({self.variant.sku})" if self.variant else ""
        return f"{self.product.name}{variant_label} x {self.quantity}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Buyurtma",
    )
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, verbose_name="Holat")
    notes = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sana")

    class Meta:
        verbose_name = "Buyurtma holati tarixi"
        verbose_name_plural = "Buyurtma holatlari tarixi"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"


class Discount(models.Model):
    DISCOUNT_TYPES = [
        ("percentage", "Foizli chegirma"),
        ("fixed", "Doimiy summa"),
    ]

    APPLY_TO = [
        ("all", "Barcha mahsulotlar"),
        ("category", "Kategoriya"),
        ("product", "Mahsulot"),
        ("manufacturer", "Brend"),
    ]

    name = models.CharField(max_length=100, verbose_name="Chegirma nomi")
    discount_type = models.CharField(
        max_length=10, choices=DISCOUNT_TYPES, default="percentage", verbose_name="Chegirma turi"
    )
    value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Chegirma qiymati",
    )
    is_additional = models.BooleanField(default=False)
    apply_to = models.CharField(
        max_length=12, choices=APPLY_TO, default="all", verbose_name="Qollash turi"
    )
    categories = models.ManyToManyField(
        "ProductCategory", blank=True, verbose_name="Kategoriyalar"
    )
    products = models.ManyToManyField("Product", blank=True, verbose_name="Mahsulotlar")
    manufacturers = models.ManyToManyField(
        "Manufacturer", blank=True, verbose_name="Brendlar"
    )
    start_date = models.DateTimeField(verbose_name="Boshlanish sanasi")
    end_date = models.DateTimeField(verbose_name="Tugash sanasi")
    max_order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Maksimal buyurtma summasi",
    )
    min_order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Minimal buyurtma summasi",
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Chegirma"
        verbose_name_plural = "Chegirmalar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.get_discount_type_display()}"

    def is_valid_for_product(self, product):
        if not self.is_active:
            return False

        now = timezone.now()
        if not (self.start_date <= now <= self.end_date):
            return False

        if self.apply_to == "all":
            return True
        if self.apply_to == "category" and product.category in self.categories.all():
            return True
        if self.apply_to == "product" and product in self.products.all():
            return True
        if self.apply_to == "manufacturer" and product.manufacturer in self.manufacturers.all():
            return True

        return False


class DeliverySettings(models.Model):
    air_delivery_rate = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Kuryer tarifi"
    )
    air_delivery_name = models.CharField(
        max_length=255, default="Kuryer", verbose_name="Kuryer nomi"
    )

    sea_delivery_rate = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Olib ketish tarifi"
    )
    sea_delivery_name = models.CharField(
        max_length=255, default="Olib ketish", verbose_name="Olib ketish nomi"
    )

    auto_delivery_rate = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Ekspress tarifi"
    )
    auto_delivery_name = models.CharField(
        max_length=255, default="Ekspress", verbose_name="Ekspress nomi"
    )

    gtd_rb_cost = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, verbose_name="Kvitansiya foizi"
    )
    gtd_rb_name = models.CharField(
        max_length=255, default="Kvitansiya", verbose_name="Kvitansiya nomi"
    )

    dt_rf_cost = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, verbose_name="Hisob-faktura foizi"
    )
    dt_rf_name = models.CharField(
        max_length=255, default="Hisob-faktura", verbose_name="Hisob-faktura nomi"
    )

    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Yetkazib berish sozlamasi"
        verbose_name_plural = "Yetkazib berish sozlamalari"

    def __str__(self):
        return "Yetkazib berish sozlamalari"


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, verbose_name="Sayt nomi")
    logo = models.ImageField(upload_to="site/", verbose_name="Logo")
    favicon = models.ImageField(upload_to="site/", blank=True, verbose_name="Favicon")
    telegram = models.CharField(max_length=200, blank=True, null=True, verbose_name="Telegram")
    whatsapp = models.CharField(max_length=300, blank=True, null=True, verbose_name="WhatsApp")
    vkontakte = models.CharField(max_length=300, blank=True, null=True, verbose_name="VK")
    youtube = models.CharField(max_length=300, blank=True, null=True, verbose_name="YouTube")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    location = models.CharField(max_length=100, verbose_name="Manzil")

    footer_text = models.TextField(null=True, blank=True, verbose_name="Footer matni")
    iframe_code = models.TextField(null=True, blank=True, verbose_name="Ofis manzili")
    checkout_text = models.TextField(null=True, blank=True, verbose_name="Checkout matni")

    meta_title = models.CharField(
        max_length=255, blank=True, verbose_name="SEO title (umumiy)"
    )
    meta_description = models.CharField(
        max_length=255, blank=True, verbose_name="SEO description (umumiy)"
    )
    meta_keywords = models.CharField(
        max_length=255, blank=True, verbose_name="SEO keywords"
    )
    og_image = models.ImageField(
        upload_to="site/", blank=True, null=True, verbose_name="OpenGraph rasm"
    )

    class Meta:
        verbose_name = "Sayt sozlamasi"
        verbose_name_plural = "Sayt sozlamalari"

    def __str__(self):
        return "Sayt sozlamalari"


class BannerImage(models.Model):
    banner = models.ImageField(upload_to="media/banners", verbose_name="Banner")
    title = models.CharField(max_length=1000, verbose_name="Sarlavha")
    text = models.TextField(verbose_name="Matn")
    benefit_title = models.TextField(verbose_name="Nega biz")
    benefit_text = models.TextField(verbose_name="Matn")
    is_active = models.BooleanField(default=False, verbose_name="Faol")

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Bannerlar"

    def __str__(self):
        return self.title


class Coin(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nomi")
    symbol = models.CharField(max_length=10, unique=True, verbose_name="Belgi")
    icon = models.ImageField(upload_to="coin_icons/", null=True, blank=True, verbose_name="Ikonka")

    class Meta:
        verbose_name = "Texnik"
        verbose_name_plural = "Texnik"

    def __str__(self):
        return self.name


class Office(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nomi")
    location = models.CharField(max_length=200, verbose_name="Manzil")
    image = models.ImageField(upload_to="offices", verbose_name="Rasm")
    email = models.CharField(max_length=100, null=True, blank=True, verbose_name="Email")
    phone = models.CharField(max_length=30, null=True, blank=True, verbose_name="Telefon")
    vkontakte = models.CharField(max_length=200, null=True, blank=True, verbose_name="VK")
    telegram = models.CharField(max_length=200, null=True, blank=True, verbose_name="Telegram")
    whatsapp = models.CharField(max_length=200, null=True, blank=True, verbose_name="WhatsApp")

    class Meta:
        verbose_name = "Ofis"
        verbose_name_plural = "Ofislar"

    def __str__(self):
        return self.name


class StaticPage(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    content = RichTextField(null=True, blank=True)
    raw_html = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Statik sahifa"
        verbose_name_plural = "Statik sahifalar"

    def __str__(self):
        return self.title


class TemplateEdit(models.Model):
    privacy_text = models.TextField(verbose_name="Maxfiylik matni", null=True, blank=True)
    about_title = models.TextField(verbose_name="Biz haqimizda sarlavha", null=True, blank=True)
    about_subtitle = models.TextField(verbose_name="Biz haqimizda subtitle", null=True, blank=True)
    payment_pay = models.TextField(verbose_name="Tolov matni", null=True, blank=True)
    payment_del = models.TextField(verbose_name="Yetkazib berish matni", null=True, blank=True)


class Cards(models.Model):
    title = models.CharField(max_length=50, null=True, blank=True)
    text = models.CharField(max_length=200, null=True, blank=True)
    icon = models.CharField(max_length=4000, null=True, blank=True)
    is_about = models.BooleanField(default=False, verbose_name="Biz haqimizda")


class AboutStat(models.Model):
    number = models.CharField(max_length=10, verbose_name="Raqam")
    text = models.CharField(max_length=100, verbose_name="Matn")


class About_page(models.Model):
    banner_bg = models.ImageField(upload_to="media/sitesettings", verbose_name="Banner", null=True)
    about_title = models.TextField(verbose_name="Sarlavha", null=True, blank=True)
    about_subtitle = models.TextField(verbose_name="Subtitle", null=True, blank=True)
    benefit_title = models.TextField(verbose_name="Afzallik sarlavha", null=True, blank=True)
    benefit_text = models.TextField(verbose_name="Afzallik matn", null=True, blank=True)
    card1 = models.TextField(verbose_name="Karta 1 matn", null=True, blank=True)
    card2 = models.TextField(verbose_name="Karta 2 matn", null=True, blank=True)
    card1_img = models.ImageField(upload_to="media/sitesettings")
    card2_img = models.ImageField(upload_to="media/sitesettings")
    statistics = models.ManyToManyField(AboutStat, related_name="stats", null=True, blank=True)
    office_title = models.TextField(verbose_name="Ofislar sarlavha", null=True, blank=True)
    office_text = models.TextField(verbose_name="Ofislar matn", null=True, blank=True)
    why_us_title = models.TextField(verbose_name="Nega biz sarlavha", null=True, blank=True)
    why_us = models.TextField(verbose_name="Nega biz", null=True, blank=True)


class PayCheck(models.Model):
    payment_pay = models.TextField(verbose_name="Tolov matni", null=True, blank=True)
    payment_title = models.TextField(verbose_name="Tolov sarlavha", null=True, blank=True)
    payment_del = models.TextField(verbose_name="Yetkazib berish matni", null=True, blank=True)
    payment_del_title = models.TextField(verbose_name="Yetkazib berish sarlavha", null=True, blank=True)
    payment_image = models.ImageField(upload_to="media/sitesettings")
    delivery_image = models.ImageField(upload_to="media/sitesettings")


class Privacy(models.Model):
    title = models.TextField()
    text = models.TextField()


class PageTitle(models.Model):
    home = models.CharField("Bosh sahifa", max_length=255, null=True, blank=True)
    catalog = models.CharField("Katalog", max_length=255, null=True, blank=True)
    detail = models.CharField("Mahsulot tafsiloti", max_length=255, null=True, blank=True)
    about = models.CharField("Biz haqimizda", max_length=255, null=True, blank=True)
    profile = models.CharField("Profil", max_length=255, null=True, blank=True)
    cart = models.CharField("Savatcha", max_length=255, null=True, blank=True)
    checkout = models.CharField("Buyurtma rasmiylash", max_length=255, null=True, blank=True)
    privacy = models.CharField("Maxfiylik siyosati", max_length=255, null=True, blank=True)
    payment_deliver = models.CharField("Tolov va yetkazib berish", max_length=255, null=True, blank=True)
    login = models.CharField("Kirish", max_length=255, null=True, blank=True)
    register = models.CharField("Royxatdan otish", max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Sahifa sarlavhasi"
        verbose_name_plural = "Sahifa sarlavhalari"

    def __str__(self):
        return "Sahifa sarlavhalari"


class DeliveryInfo(models.Model):
    title = models.CharField(
        max_length=255, default="Yetkazib berish haqida"
    )
    courier_title = models.CharField(
        max_length=255, default="Kuryer (2-5 kun)"
    )
    air_title = models.CharField(
        max_length=255, default="Ekspress (1-2 kun)"
    )
    sea_title = models.CharField(
        max_length=255, default="Olib ketish (shaxsiy)"
    )

    main_text = models.CharField(
        max_length=900, null=True, blank=True, verbose_name="Asosiy matn", default=""
    )
    free_shipping_text = models.CharField(
        max_length=255, default="1000000 so'mdan yuqori buyurtma uchun bepul"
    )
    paid_shipping_text = models.CharField(
        max_length=255, default="1000000 so'mgacha: 25000-50000 so'm"
    )

    important_info_title = models.CharField(
        max_length=255, default="Muhim:"
    )
    important_info_body = models.TextField(
        default="Har bir mahsulot sifat nazoratidan otadi. Original va kafolatli mahsulotlar."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Yetkazib berish (kontent)"
        verbose_name_plural = "Yetkazib berish (kontent)"

    def __str__(self):
        return f"Yetkazib berish ({self.id})"


class OrderStatusRule(models.Model):
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    days_after = models.PositiveIntegerField(
        help_text="Necha kundan keyin ushbu holatga otadi?"
    )
    order_priority = models.PositiveIntegerField(
        default=0, help_text="Ustuvorlik raqami (kichikdan boshlanadi)"
    )
    is_active = models.BooleanField(default=True)
    immediate = models.BooleanField(
        default=False, verbose_name="Darhol qollansinmi?"
    )

    class Meta:
        verbose_name = "Buyurtma holati qoidasi"
        verbose_name_plural = "Buyurtma holati qoidalari"

    def __str__(self):
        return f"{self.days_after} kun -> {self.get_status_display()}"
