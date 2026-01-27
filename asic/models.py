from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .utils import calculate_product_discount,get_product_discounts
from ckeditor.fields import RichTextField

class Manufacturer(models.Model):
    """Производители"""
    name = models.CharField(max_length=100, verbose_name="Название")
    logo = models.ImageField(upload_to='manufacturers/', verbose_name="Логотип")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.name

class Profile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    name = models.CharField(max_length=200,null=True,blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    father_name = models.CharField(max_length=150, blank=True)
    address_street = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    home = models.CharField(max_length=100,null=True,blank=True)
    address_city = models.CharField(max_length=100, blank=True, null=True)
    address_region = models.CharField(max_length=100, blank=True, null=True)
    address_postal_code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user.username}"

class ProductCategory(models.Model):
    """Категории продуктов"""
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Слаг")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родительская категория")

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return self.name

class Product(models.Model):
    """ASIC майнеры (оптимизированная модель)"""

    HASH_UNITS = [
        ('TH', 'TH/s'),
        ('GH', 'GH/s'),
        ('MH', 'MH/s'),
    ]
    hash_unit = models.CharField(max_length=2, choices=HASH_UNITS, default='TH')

    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Слаг")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена")
    old_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True, verbose_name="Старая цена")
    hash_rate = models.IntegerField(blank=True, verbose_name="Хешрейт")
    power_consumption = models.IntegerField(blank=True, verbose_name="Потребление энергии")
    algorithm = models.CharField(max_length=100, blank=True, verbose_name="Алгоритм")
    description = models.TextField(verbose_name="Описание")
    specifications = models.TextField(blank=True, verbose_name="Характеристики")
    temprature = models.CharField(max_length=200,null=True,blank=True)
    images = models.ImageField(upload_to="media/products",null=True,blank=True, verbose_name="Основное изображение")
    image2 = models.ImageField(upload_to="media/products",null=True,blank=True, verbose_name="Дополнительное изображение 1")
    image3 = models.ImageField(upload_to="media/products",null=True,blank=True, verbose_name="Дополнительное изображение 2")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    coins = models.ManyToManyField('Coin', related_name='products',blank=True, verbose_name="Монеты")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    @property
    def current_price(self):
        """Текущая цена с учетом активных скидок"""
        discount_info = calculate_product_discount(self, self.price)
        return discount_info['discounted_price']

    def get_discount_info(self):
        """Возвращает информацию о скидке для товара"""
        return calculate_product_discount(self, self.price)

    def has_discount(self):
        """Проверяет наличие скидки на товар"""
        return bool(get_product_discounts(self))

    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"


class Order(models.Model):
    DELIVERY_TYPES = [
        ('air', 'Авиадоставка'),
        ('sea', 'Морская доставка'),
        ('auto', 'Авто доставка'),   # 🔥 qo‘shildi
    ]

    DOCUMENT_TYPES = [
        ('gtd_rb', 'GTD RB'),
        ('dt_rf', 'DT RF'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новый заказ'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('customs', 'На таможне'),                  # 🔥 qo‘shildi
        ('sorting', 'В сортировочном центре'),      # 🔥 qo‘shildi
        ('delivering', 'Доставляется'),             # 🔥 qo‘shildi
        ('pickup_ready', 'Готов к выдаче'),         # 🔥 qo‘shildi
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Номер заказа")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPES, verbose_name="Тип доставки")
    delivery_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Стоимость доставки")
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES, verbose_name="Тип документа")
    document_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Стоимость документов")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Промежуточная сумма")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Процент скидки")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Сумма скидки")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Итоговая сумма")
    payment_id = models.CharField(max_length=100, blank=True, verbose_name="ID платежа")
    payment_status = models.CharField(max_length=20, default='pending', verbose_name="Статус оплаты")
    shipping_address = models.TextField(verbose_name="Адрес доставки")
    billing_address = models.TextField(blank=True, verbose_name="Платежный адрес")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    last_status_update = models.DateTimeField(auto_now_add=True, null=True,blank=True,verbose_name="Дата последнего изменения статуса")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.order_number} - {self.user.username}"

    def get_dynamic_delivery_name(self):
        """DeliverySettings dagi nomni qaytaradi"""
        settings = DeliverySettings.objects.filter(is_active=True).first()
        if not settings:
            return self.get_delivery_type_display()

        if self.delivery_type == "air":
            return settings.air_delivery_name
        elif self.delivery_type == "sea":
            return settings.sea_delivery_name
        elif self.delivery_type == "auto":
            return settings.auto_delivery_name
        return self.get_delivery_type_display()

    def get_dynamic_document_name(self):
        """DeliverySettings dagi document nomini qaytaradi"""
        settings = DeliverySettings.objects.filter(is_active=True).first()
        if not settings:
            return self.get_document_type_display()

        if self.document_type == "gtd_rb":
            return settings.gtd_rb_name
        elif self.document_type == "dt_rf":
            return settings.dt_rf_name
        return self.get_document_type_display()
    
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            from .models import OrderStatusRule
            from django.utils import timezone

            # faqat "immediate=True" bo'lgan qoidalarni tekshiramiz
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
    """Позиции заказа"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    original_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Yangi
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def get_cost(self):
        return self.quantity*self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class OrderStatusHistory(models.Model):
    """История статусов заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history', verbose_name="Заказ")
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, verbose_name="Статус")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name = "История статуса заказа"
        verbose_name_plural = "История статусов заказов"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"

class Discount(models.Model):
    """Основная модель для скидок"""
    DISCOUNT_TYPES = [
        ('percentage', 'Процентная скидка'),
        ('fixed', 'Фиксированная сумма'),
    ]

    APPLY_TO = [
        ('all', 'Все товары'),
        ('category', 'Конкретная категория'),
        ('product', 'Конкретный товар'),
        ('manufacturer', 'Производитель'),
    ]

    name = models.CharField(max_length=100, verbose_name="Название скидки")
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='percentage', verbose_name="Тип скидки")
    value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Значение скидки"
    )
    is_additional = models.BooleanField(default=False)
    apply_to = models.CharField(max_length=12, choices=APPLY_TO, default='all', verbose_name="Применять к")
    categories = models.ManyToManyField(
        'ProductCategory',
        blank=True,
        verbose_name="Категории"
    )
    products = models.ManyToManyField(
        'Product',
        blank=True,
        verbose_name="Товары"
    )
    manufacturers = models.ManyToManyField(
        'Manufacturer',
        blank=True,
        verbose_name="Производители"
    )
    start_date = models.DateTimeField(verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    max_order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Максимальная сумма заказа"
    )
    min_order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Минимальная сумма заказа"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_discount_type_display()}"

    def is_valid_for_product(self, product):
        """Проверяет применимость скидки к товару"""
        if not self.is_active:
            return False

        now = timezone.now()
        if not (self.start_date <= now <= self.end_date):
            return False

        if self.apply_to == 'all':
            return True
        elif self.apply_to == 'category' and product.category in self.categories.all():
            return True
        elif self.apply_to == 'product' and product in self.products.all():
            return True
        elif self.apply_to == 'manufacturer' and product.manufacturer in self.manufacturers.all():
            return True

        return False

class DeliverySettings(models.Model):
    """Настройки доставки"""
    air_delivery_rate = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Тариф авиадоставки"
    )
    air_delivery_name = models.CharField(
        max_length=255, default="Авиадоставка", verbose_name="Название тарифа авиадоставки"
    )

    sea_delivery_rate = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Тариф морской доставки"
    )
    sea_delivery_name = models.CharField(
        max_length=255, default="Морская доставка", verbose_name="Название тарифа морской доставки"
    )

    auto_delivery_rate = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Тариф Авто доставки"
    )
    auto_delivery_name = models.CharField(
        max_length=255, default="Морская доставка", verbose_name="Название тарифа Авто доставки"
    )

    gtd_rb_cost = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.0, verbose_name="Процент GTD/RB"
    )
    gtd_rb_name = models.CharField(
        max_length=255, default="GTD/RB", verbose_name="Название GTD/RB"
    )

    dt_rf_cost = models.DecimalField(
        max_digits=5, decimal_places=2, default=3.0, verbose_name="Процент DT/RF"
    )
    dt_rf_name = models.CharField(
        max_length=255, default="DT/RF", verbose_name="Название DT/RF"
    )

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Настройка доставки"
        verbose_name_plural = "Настройки доставки"

    def __str__(self):
        return "Настройки доставки"



class SiteSettings(models.Model):
    """Общие настройки сайта"""
    site_name = models.CharField(max_length=100, verbose_name="Название сайта")
    logo = models.ImageField(upload_to='site/', verbose_name="Логотип")
    favicon = models.ImageField(upload_to='site/', blank=True, verbose_name="Фавикон")
    telegram = models.CharField(max_length=200, blank=True,null=True, verbose_name="Telegram")
    whatsapp = models.CharField(max_length=300, blank=True,null=True, verbose_name="WhatsApp")
    vkontakte = models.CharField(max_length=300, blank=True,null=True, verbose_name="ВКонтакте")
    youtube = models.CharField(max_length=300, blank=True,null=True, verbose_name="YouTube")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    location = models.CharField(max_length=100, verbose_name="Адрес")

    footer_text = models.TextField(null=True,blank=True,verbose_name="Footer text")
    iframe_code = models.TextField(null=True,blank=True,verbose_name="Адрес офисы")

    checkout_text = models.TextField(null=True,blank=True,verbose_name='текст оформления заказа')
    class Meta:
        verbose_name = "Настройка сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

class BannerImage(models.Model):
    """Баннеры"""
    banner = models.ImageField(upload_to='media/banners', verbose_name="Баннер")
    title = models.CharField(max_length=1000, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    benefit_title = models.TextField(verbose_name="Почему выбирают нас")
    benefit_text = models.TextField(verbose_name="Текст")
    is_active = models.BooleanField(default=False, verbose_name="Активен")

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"

    def __str__(self):
        return self.title

class Coin(models.Model):
    """Криптовалюты"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    symbol = models.CharField(max_length=10, unique=True, verbose_name="Символ")
    icon = models.ImageField(upload_to='coin_icons/', null=True, blank=True, verbose_name="Иконка")

    class Meta:
        verbose_name = "Монета"
        verbose_name_plural = "Монеты"

    def __str__(self):
        return self.name

class Office(models.Model):
    """Офисы"""
    name = models.CharField(max_length=50, verbose_name="Название")
    location = models.CharField(max_length=200, verbose_name="Адрес")
    image = models.ImageField(upload_to='offices', verbose_name="Изображение")
    email = models.CharField(max_length=100, null=True,blank=True, verbose_name="Email")
    phone = models.CharField(max_length=30, null=True,blank=True, verbose_name="Телефон")
    vkontakte = models.CharField(max_length=200, null=True,blank=True, verbose_name="ВКонтакте")
    telegram = models.CharField(max_length=200, null=True,blank=True, verbose_name="Telegram")
    whatsapp = models.CharField(max_length=200,  null=True,blank=True,verbose_name="WhatsApp")


    class Meta:
        verbose_name = "Офис"
        verbose_name_plural = "Офисы"

    def __str__(self):
        return self.name


class StaticPage(models.Model):
    slug = models.SlugField(unique=True)  # misol: privacy-policy
    title = models.CharField(max_length=200)
    content = RichTextField(null=True,blank=True)
    raw_html = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.title


class TemplateEdit(models.Model):
    privacy_text = models.TextField(verbose_name='privacy text',null=True,blank=True)
    about_title = models.TextField(verbose_name='About title',null=True,blank=True)
    about_subtitle = models.TextField(verbose_name='About subtitle',null=True,blank=True)

    payment_pay = models.TextField(verbose_name='Оплата text',null=True,blank=True)
    payment_del = models.TextField(verbose_name='Доставка  text',null=True,blank=True)


class Cards(models.Model):
    title = models.CharField(max_length=50,null=True,blank=True)
    text = models.CharField(max_length=200,null=True,blank=True)
    icon = models.CharField(max_length=4000,null=True,blank=True)
    is_about = models.BooleanField(default=False,verbose_name='О компании')

class AboutStat(models.Model):
    number = models.CharField(max_length=10, verbose_name='число')
    text  = models.CharField(max_length=10)

class About_page(models.Model):
    banner_bg = models.ImageField(upload_to='media/sitesettings', verbose_name='Banner',null=True)
    about_title = models.TextField(verbose_name='About title',null=True,blank=True)
    about_subtitle = models.TextField(verbose_name='About subtitle',null=True,blank=True)
    benefit_title = models.TextField(verbose_name='преимущества title',null=True,blank=True)
    benefit_text = models.TextField(verbose_name='преимущества text',null=True,blank=True)
    card1 = models.TextField(verbose_name='Card 1 text',null=True,blank=True)
    card2 = models.TextField(verbose_name='Card 2 text',null=True,blank=True)
    card1_img = models.ImageField(upload_to='media/sitesettings')
    card2_img = models.ImageField(upload_to='media/sitesettings')
    statistics = models.ManyToManyField(AboutStat, related_name='stats',null=True,blank=True)
    office_title =  models.TextField(verbose_name='Наши офисы title',null=True,blank=True)
    office_text =  models.TextField(verbose_name='Наши офисы text',null=True,blank=True)
    why_us_title = models.TextField(verbose_name='почему мы title',null=True,blank=True)
    why_us = models.TextField(verbose_name='почему мы',null=True,blank=True)

class PayCheck(models.Model):
    payment_pay = models.TextField(verbose_name='Оплата text',null=True,blank=True)
    payment_title = models.TextField(verbose_name='Оплата title',null=True,blank=True)
    payment_del = models.TextField(verbose_name='Доставка  text',null=True,blank=True)
    payment_del_title = models.TextField(verbose_name='Доставка  title',null=True,blank=True)
    payment_image = models.ImageField(upload_to='media/sitesettings')
    delivery_image = models.ImageField(upload_to='media/sitesettings')


class Privacy(models.Model):
    title = models.TextField()
    text = models.TextField()

# core/models.py
from django.db import models

class PageTitle(models.Model):
    home = models.CharField("Главная страница", max_length=255, null=True, blank=True)
    catalog = models.CharField("Каталог", max_length=255, null=True, blank=True)
    detail = models.CharField("Детали продукта", max_length=255, null=True, blank=True)
    about = models.CharField("О нас", max_length=255, null=True, blank=True)
    profile = models.CharField("Профиль", max_length=255, null=True, blank=True)
    cart = models.CharField("Корзина", max_length=255, null=True, blank=True)
    checkout = models.CharField("Оформление заказа", max_length=255, null=True, blank=True)
    privacy = models.CharField("Политика конфиденциальности", max_length=255, null=True, blank=True)
    payment_deliver = models.CharField("Оплата и доставка", max_length=255, null=True, blank=True)
    login = models.CharField("Login", max_length=255, null=True, blank=True)
    register = models.CharField("Register", max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Заголовок страниц"
        verbose_name_plural = "Заголовки страниц"

    def __str__(self):
        return "Заголовки сайта"

from django.db import models

class DeliveryInfo(models.Model):
    # Asosiy sarlavha
    title = models.CharField(max_length=255, default="Информация о доставке")

    # Yetkazib berish usullari
    courier_title = models.CharField(max_length=255, default="Курьерская доставка (5-7 дней)")
    air_title = models.CharField(max_length=255, default="Авиа экспресс (3-5 дней)")
    sea_title = models.CharField(max_length=255, default="Морская доставка (15-30 дней)")

    main_text = models.CharField(max_length=900,null=True,blank=True,verbose_name="текст выше",default="text")
    # Narxlar bo‘limi
    free_shipping_text = models.CharField(
        max_length=255,
        default="Бесплатно при заказе от $2000"
    )
    paid_shipping_text = models.CharField(
        max_length=255,
        default="До $2000 - $50-150 в зависимости от региона"
    )

    # Muhim ma'lumot
    important_info_title = models.CharField(
        max_length=255,
        default="Важная информация:"
    )
    important_info_body = models.TextField(
        default="Все товары проходят предпродажную проверку и тестирование. "
                "Гарантируем работоспособность и соответствие заявленным характеристикам."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Доставка (контент)"
        verbose_name_plural = "Доставка (контент)"

    def __str__(self):
        return f"Информация о доставке ({self.id})"


class OrderStatusRule(models.Model):
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    days_after = models.PositiveIntegerField(help_text="Сколько дней потребуется, чтобы достичь этого статуса?")
    order_priority = models.PositiveIntegerField(default=0, help_text="Порядковый номер (сначала выполняется наименьший)")
    is_active = models.BooleanField(default=True)
    immediate = models.BooleanField(
        default=False,
        verbose_name="Применять сразу при создании заказа?"
    )    
def __str__(self):
        return f"Через {self.days_after} день  → {self.get_status_display()}"
