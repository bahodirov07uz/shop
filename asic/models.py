from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .utils import calculate_product_discount,get_product_discounts

class Manufacturer(models.Model):
    """Ishlab chiqaruvchilar modeli"""
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='manufacturers/')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"
    
class ProductCategory(models.Model):
    """Mahsulot kategoriyalari"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """ASIC maynerlar modeli (optimallashtirilgan)"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    old_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    hash_rate = models.CharField(max_length=100, blank=True)
    power_consumption = models.CharField(max_length=100, blank=True)
    algorithm = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    specifications = models.TextField(blank=True)
    images = models.ImageField(upload_to="media/products",null=True,blank=True)
    image2 = models.ImageField(upload_to="media/products",null=True,blank=True)
    image3 = models.ImageField(upload_to="media/products",null=True,blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    coins = models.ManyToManyField('Coin', related_name='products',null=True,blank=True)  
    
    @property
    def current_price(self):
        """Aktiv chegirmalarni hisobga olgan holda joriy narx"""
        discount_info = calculate_product_discount(self, self.price)
        return discount_info['discounted_price']
    
    def get_discount_info(self):
        """Mahsulot uchun chegirma ma'lumotlarini qaytaradi"""
        return calculate_product_discount(self, self.price)
    
    def has_discount(self):
        """Mahsulotda chegirma borligini tekshiradi"""
        return bool(get_product_discounts(self))
    
    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"

class Order(models.Model):
    DELIVERY_TYPES = [
        ('air', 'Авиакурьер'),
        ('sea', 'По морю'),
    ]
    
    DOCUMENT_TYPES = [
        ('gtd_rb', 'GTD RB'),
        ('dt_rf', 'DT RF'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Новый заказ'),
        ('processing', 'Подготовка'),
        ('shipped', 'Отправил'),
        ('ready', 'Готов отправить'),
        ('completed', 'Завершенный'),
        ('cancelled', 'Отменено'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPES)
    delivery_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    document_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_id = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Buyurtma #{self.order_number} - {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    
    def get_cost(self):
        return self.quantity*self.price
    
class OrderStatusHistory(models.Model):
    """Buyurtma statusi tarixi"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"

class Discount(models.Model):
    """Chegirmalar uchun asosiy model"""
    DISCOUNT_TYPES = [
        ('percentage', 'Foizli chegirma'),
        ('fixed', 'Aniq summa'),
    ]
    
    APPLY_TO = [
        ('all', 'Barcha mahsulotlar'),
        ('category', 'Maxsus kategoriya'),
        ('product', 'Maxsus mahsulot'),
        ('manufacturer', 'Ishlab chiqaruvchi'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Chegirma nomi")
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='percentage')
    value = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Chegirma qiymati"
    )
    apply_to = models.CharField(max_length=12, choices=APPLY_TO, default='all')
    categories = models.ManyToManyField(
        'ProductCategory', 
        blank=True,
        verbose_name="Kategoriyalar"
    )
    products = models.ManyToManyField(
        'Product', 
        blank=True,
        verbose_name="Mahsulotlar"
    )
    manufacturers = models.ManyToManyField(
        'Manufacturer',
        blank=True,
        verbose_name="Ishlab chiqaruvchilar"
    )
    start_date = models.DateTimeField(verbose_name="Boshlanish sanasi")
    end_date = models.DateTimeField(verbose_name="Tugash sanasi")
    min_order_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        verbose_name="Minimal buyurtma summasi"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Chegirma"
        verbose_name_plural = "Chegirmalar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_discount_type_display()}"
    
    def is_valid_for_product(self, product):
        """Mahsulotga chegirma qo'llanilishini tekshiradi"""
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
    """Yetkazib berish narxlari sozlamalari"""
    air_delivery_rate = models.DecimalField(max_digits=12, decimal_places=2)
    sea_delivery_rate = models.DecimalField(max_digits=12, decimal_places=2)
    gtd_rb_cost = models.DecimalField(max_digits=12, decimal_places=2)
    dt_rf_cost = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Yetkazib berish sozlamalari"


class SiteSettings(models.Model):
    """Sayt umumiy sozlamalari"""
    site_name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='site/')
    favicon = models.ImageField(upload_to='site/', blank=True)
    telegram = models.CharField(max_length=200, blank=True,null=True)
    whatsapp = models.CharField(max_length=300, blank=True,null=True)
    vkontakte = models.CharField(max_length=300, blank=True,null=True)
    youtube = models.CharField(max_length=300, blank=True,null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
     
    
    def __str__(self):
        return "Sayt sozlamalari"
    
class BannerImage(models.Model):
    banner = models.ImageField(upload_to='media/banners')
    title = models.CharField(max_length=1000)
    text = models.TextField()
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
class Coin(models.Model):
    name = models.CharField(max_length=50, unique=True)
    symbol = models.CharField(max_length=10, unique=True)
    icon = models.ImageField(upload_to='coin_icons/', null=True, blank=True)

    def __str__(self):
        return self.name

class Office(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='offices')
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    vkontakte = models.CharField(max_length=200)
    telegram = models.CharField(max_length=200)
    whatsapp = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name