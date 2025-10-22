from django.contrib import admin
from .models import (
    Manufacturer, ProductCategory, Product,
    Order, OrderStatusHistory, Discount,
    DeliverySettings, SiteSettings, OrderItem, 
    BannerImage, Coin, Office, StaticPage, 
    Cards, TemplateEdit, About_page, PayCheck, 
    Privacy, Profile,OrderStatusRule, AboutStat
)
from import_export.admin import ImportExportModelAdmin
from .resources import ProductResource

# ===== ПРОИЗВОДИТЕЛИ =====
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)
    
    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'


from django.contrib import admin
from .models import DeliveryInfo


@admin.register(DeliveryInfo)
class DeliveryInfoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "courier_title",
        "air_title",
        "sea_title",
        "updated_at",
    )
    # Admin sahifasida qulay tahrirlash uchun
    fieldsets = (
        (None, {
            "fields": (
                ("title","main_text"),
                ("courier_title", "air_title", "sea_title"),
                ("free_shipping_text", "paid_shipping_text"),
                ("important_info_title", "important_info_body"),
            )
        }),
    )
    search_fields = ("title", "courier_title", "air_title", "sea_title")
    ordering = ("-updated_at",)


# ===== КАТЕГОРИИ ТОВАРОВ =====
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('parent',)
    ordering = ('name',)
    
    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'

# ===== ТОВАРЫ =====
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('name', 'manufacturer', 'category', 'price', 'stock', 'is_active')
    list_editable = ('price', 'stock', 'is_active')
    list_filter = ('is_active', 'is_featured', 'category', 'manufacturer')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('manufacturer', 'category')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

# ===== ЗАКАЗЫ =====
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at', 'items_count')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'items_list')
    autocomplete_fields = ('user',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [OrderItemInline]

    actions = ['set_status_new', 'set_status_processing', 'set_status_shipped',
               'set_status_ready', 'set_status_completed', 'set_status_cancelled']  # 🔥 qo‘shildi

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Количество товаров'

    def items_list(self, obj):
        return ", ".join([f"{item.product.name} ({item.quantity})" for item in obj.items.all()])
    items_list.short_description = 'Состав заказа'

    # === BULK ACTIONS ===
    def set_status_new(self, request, queryset):
        queryset.update(status='new')
    set_status_new.short_description = "Изменить статус на: Новый заказ"

    def set_status_processing(self, request, queryset):
        queryset.update(status='processing')
    set_status_processing.short_description = "Изменить статус на: В обработке"

    def set_status_shipped(self, request, queryset):
        queryset.update(status='shipped')
    set_status_shipped.short_description = "Изменить статус на: Отправлен"

    def set_status_ready(self, request, queryset):
        queryset.update(status='ready')
    set_status_ready.short_description = "Изменить статус на: Готов к отправке"

    def set_status_completed(self, request, queryset):
        queryset.update(status='completed')
    set_status_completed.short_description = "Изменить статус на: Завершен"

    def set_status_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    set_status_cancelled.short_description = "Изменить статус на: Отменен"


from .models import OrderStatusRule

@admin.register(OrderStatusRule)
class OrderStatusRuleAdmin(admin.ModelAdmin):
    list_display = ("status", "days_after",'order_priority', "is_active")
    list_editable = ("days_after",'order_priority', "is_active")
    ordering = ("days_after",)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('days_after')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity', 'order_status')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name')
    raw_id_fields = ('order', 'product')
    
    def order_status(self, obj):
        return obj.order.status
    order_status.short_description = 'Статус заказа'
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

# ===== ИСТОРИЯ СТАТУСОВ ЗАКАЗОВ =====
@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('order__order_number',)
    autocomplete_fields = ('order',)
    
    class Meta:
        verbose_name = 'История статуса заказа'
        verbose_name_plural = 'История статусов заказов'

# ===== СКИДКИ =====

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        'name',
	'value',
        'min_order_amount',
        'max_order_amount',
        'is_active',
        'is_additional',
    )
    list_editable = ('value','min_order_amount', 'max_order_amount', 'is_active', 'is_additional')
    
    search_fields = ('name',)
    filter_horizontal = ('categories', 'products', 'manufacturers')
    readonly_fields = ('created_at',)
    ordering = ('-id',)

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'


# ===== НАСТРОЙКИ ДОСТАВКИ (ПЛАТЕЖИ) =====
@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ('air_delivery_rate', 'sea_delivery_rate', 'gtd_rb_cost', 'dt_rf_cost', 'is_active')
    list_editable = ('is_active',)
    ordering = ('-id',)
    
    class Meta:
        verbose_name = 'Настройка доставки'
        verbose_name_plural = 'Настройки доставки'

# ===== НАСТРОЙКИ САЙТА (АККАУНТЫ) =====
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone', 'telegram', 'whatsapp', 'vkontakte')
    ordering = ('site_name',)
    
    class Meta:
        verbose_name = 'Настройка сайта'
        verbose_name_plural = 'Настройки сайта'

# ===== ПРОФИЛИ ПОЛЬЗОВАТЕЛЕЙ (АККАУНТЫ) =====
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'name', 'email')
    search_fields = ('user__username', 'phone', 'name', 'user__email')
    raw_id_fields = ('user',)
    list_filter = ('user__is_active',)
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

# ===== ОФИСЫ (АККАУНТЫ В СОЦСЕТЯХ) =====
@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone', 'email', 'telegram', 'whatsapp', 'vkontakte')
    list_filter = ('name',)
    search_fields = ('name', 'location', 'phone')
    
    class Meta:
        verbose_name = 'Офис'
        verbose_name_plural = 'Офисы'

# ===== БАННЕРЫ =====
@admin.register(BannerImage)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title', 'text')
    
    actions = ['activate_selected', 'deactivate_selected']
    
    def activate_selected(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, "Можно активировать только один баннер одновременно.", level='ERROR')
            return
        
        banner = queryset.first()
        banner.is_active = True
        banner.save()
        self.message_user(request, f"Активирован баннер: {banner.title}")
    
    activate_selected.short_description = "Активировать выбранный баннер"
    
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {updated} баннеров")
    
    deactivate_selected.short_description = "Деактивировать выбранные баннеры"
    
    def save_model(self, request, obj, form, change):
        if obj.is_active:
            BannerImage.objects.exclude(pk=obj.pk).filter(is_active=True).update(is_active=False)
        super().save_model(request, obj, form, change)
    
    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'

# ===== МОНЕТЫ =====
@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    
    class Meta:
        verbose_name = 'Монета'
        verbose_name_plural = 'Монеты'

# ===== СТАТИЧЕСКИЕ СТРАНИЦЫ =====
@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'slug')
    
    class Meta:
        verbose_name = 'Статическая страница'
        verbose_name_plural = 'Статические страницы'

# ===== КАРТОЧКИ =====
@admin.register(Cards)
class CardsAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "icon", "is_about")
    list_filter = ("is_about",)
    search_fields = ("title", "text")
    
    class Meta:
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'

# ===== РЕДАКТИРОВАНИЕ ШАБЛОНОВ =====

# ===== СТРАНИЦА "О НАС" =====
@admin.register(About_page)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('about_title', 'benefit_title')
    filter_horizontal = ('statistics',)
    
    class Meta:
        verbose_name = 'Страница "О нас"'
        verbose_name_plural = 'Страницы "О нас"'

# ===== ОПЛАТА И ДОСТАВКА =====
@admin.register(PayCheck)
class PayCheckAdmin(admin.ModelAdmin):
    list_display = ("id",)
    
    class Meta:
        verbose_name = 'Оплата и доставка'
        verbose_name_plural = 'Оплата и доставка'

# ===== ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ =====
@admin.register(Privacy)
class PrivacyAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title", "text")
    
    class Meta:
        verbose_name = 'Политика конфиденциальности'
        verbose_name_plural = 'Политики конфиденциальности'

# ===== СТАТИСТИКА О НАС =====
@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    list_display = ("number", "text")
    search_fields = ("number", "text")
    
    class Meta:
        verbose_name = 'Статистика о нас'
        verbose_name_plural = 'Статистика о нас'


from .models import PageTitle

@admin.register(PageTitle)
class PageTitleAdmin(admin.ModelAdmin):
    list_display = ['id']


# Устанавливаем русские названия для моделей в админ-панели
Manufacturer._meta.verbose_name = 'Производитель'
Manufacturer._meta.verbose_name_plural = 'Производители'

ProductCategory._meta.verbose_name = 'Категория товара'
ProductCategory._meta.verbose_name_plural = 'Категории товаров'

Product._meta.verbose_name = 'Товар'
Product._meta.verbose_name_plural = 'Товары'

Order._meta.verbose_name = 'Заказ'
Order._meta.verbose_name_plural = 'Заказы'

OrderItem._meta.verbose_name = 'Позиция заказа'
OrderItem._meta.verbose_name_plural = 'Позиции заказа'

OrderStatusHistory._meta.verbose_name = 'История статуса заказа'
OrderStatusHistory._meta.verbose_name_plural = 'История статусов заказов'

Discount._meta.verbose_name = 'Скидка'
Discount._meta.verbose_name_plural = 'Скидки'

DeliverySettings._meta.verbose_name = 'Настройка доставки'
DeliverySettings._meta.verbose_name_plural = 'Настройки доставки'

SiteSettings._meta.verbose_name = 'Настройка сайта'
SiteSettings._meta.verbose_name_plural = 'Настройки сайта'

Profile._meta.verbose_name = 'Профиль'
Profile._meta.verbose_name_plural = 'Профили'

BannerImage._meta.verbose_name = 'Баннер'
BannerImage._meta.verbose_name_plural = 'Баннеры'

Coin._meta.verbose_name = 'Монета'
Coin._meta.verbose_name_plural = 'Монеты'

Office._meta.verbose_name = 'Офис'
Office._meta.verbose_name_plural = 'Офисы'

StaticPage._meta.verbose_name = 'Статическая страница'
StaticPage._meta.verbose_name_plural = 'Статические страницы'

Cards._meta.verbose_name = 'Карточка'
Cards._meta.verbose_name_plural = 'Карточки'


About_page._meta.verbose_name = 'Страница "О нас"'
About_page._meta.verbose_name_plural = 'Страницы "О нас"'

PayCheck._meta.verbose_name = 'Оплата и доставка'
PayCheck._meta.verbose_name_plural = 'Оплата и доставка'

Privacy._meta.verbose_name = 'Политика конфиденциальности'
Privacy._meta.verbose_name_plural = 'Политики конфиденциальности'

AboutStat._meta.verbose_name = 'Статистика о нас'
AboutStat._meta.verbose_name_plural = 'Статистика о нас'
