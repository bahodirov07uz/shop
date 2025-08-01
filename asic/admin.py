from django.contrib import admin
from .models import (
    Manufacturer, ProductCategory, Product,
    Order, OrderStatusHistory, Discount,
    DeliverySettings, SiteSettings, OrderItem, BannerImage, Coin, Office
)
from import_export.admin import ExportMixin
from .resources import ProductResource

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')  # Отображаемые поля в списке
    list_editable = ('is_active',)  # Поля, доступные для редактирования прямо в списке
    search_fields = ('name',)  # Поля для поиска
    list_filter = ('is_active',)  # Фильтры справа
    ordering = ('name',)  # Сортировка по умолчанию


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')  # Название и родительская категория
    search_fields = ('name',)  # Поиск по названию
    prepopulated_fields = {'slug': ('name',)}  # Автозаполнение slug из названия
    autocomplete_fields = ('parent',)  # Автодополнение для родительской категории
    ordering = ('name',)  # Сортировка по названию


from import_export.admin import ImportExportModelAdmin

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('name', 'manufacturer', 'category', 'price', 'stock', 'is_active')
    list_editable = ('price', 'stock', 'is_active')  # Редактируемые поля в списке
    list_filter = ('is_active', 'is_featured', 'category', 'manufacturer')
    search_fields = ('name', 'description')  # Поиск по названию и описанию
    prepopulated_fields = {'slug': ('name',)}  # Автозаполнение slug
    readonly_fields = ('created_at', 'updated_at')  # Только для чтения
    autocomplete_fields = ('manufacturer', 'category')  # Автодополнение
    date_hierarchy = 'created_at'  # Навигация по датам
    ordering = ('-created_at',)  # Сортировка по дате создания (новые сначала)


class OrderItemInline(admin.TabularInline):  # Встроенное отображение товаров в заказе
    model = OrderItem
    extra = 0  # Не показывать дополнительные пустые формы
    readonly_fields = ('product', 'price', 'quantity')  # Только для чтения
    can_delete = False  # Запретить удаление
    
    def has_add_permission(self, request, obj=None):
        return False  # Запретить добавление новых товаров

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at', 'items_count')
    list_filter = ('status', 'created_at')  # Фильтры по статусу и дате
    search_fields = ('order_number', 'user__username')  # Поиск по номеру и пользователю
    readonly_fields = ('created_at', 'updated_at', 'order_number', 'items_list')
    autocomplete_fields = ('user',)  # Автодополнение пользователя
    date_hierarchy = 'created_at'  # Навигация по датам
    ordering = ('-created_at',)  # Сортировка (новые сначала)
    inlines = [OrderItemInline]  # Встроенное отображение товаров
    actions = ['mark_as_completed', 'mark_as_shipped', 'mark_as_customs']  # Действия
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Финансовая информация', {
            'fields': ('subtotal', 'delivery_cost', 'document_cost', 'total')
        }),
        ('Информация о доставке', {
            'fields': ('delivery_type', 'document_type', 'shipping_address', 'billing_address')
        }),
        ('Дополнительная информация', {
            'fields': ('payment_status', 'notes', 'created_at', 'updated_at')
        }),
    )
    
    def items_count(self, obj):
        return obj.items.count()  # Количество товаров в заказе
    items_count.short_description = 'Товары'

    def items_list(self, obj):
        return ", ".join([f"{item.product.name} ({item.quantity})" for item in obj.items.all()])
    items_list.short_description = 'Состав заказа'

    @admin.action(description="Отметить выбранные заказы как выполненные")
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} заказы отмечены как выполненные")

    @admin.action(description="Отметить выбранные заказы как отправленные")
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f"{updated} заказы отмечены как отправленные")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity', 'order_status')
    list_filter = ('order__status',)  # Фильтр по статусу заказа
    search_fields = ('order__order_number', 'product__name')  # Поиск по номеру и названию
    raw_id_fields = ('order', 'product')  # Поля с raw ID
    
    def order_status(self, obj):
        return obj.order.status  # Статус родительского заказа
    order_status.short_description = 'Статус заказа'
    order_status.admin_order_field = 'order__status'

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at')  # История статусов
    list_filter = ('status',)  # Фильтр по статусу
    search_fields = ('order__order_number',)  # Поиск по номеру заказа
    autocomplete_fields = ('order',)  # Автодополнение заказа


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'value', 'apply_to', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'discount_type', 'apply_to')  # Фильтры
    search_fields = ('name',)  # Поиск по названию
    filter_horizontal = ('categories', 'products', 'manufacturers')  # Горизонтальные фильтры
    readonly_fields = ('created_at',)  # Только для чтения
    ordering = ('-start_date',)  # Сортировка по дате начала


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ('air_delivery_rate', 'sea_delivery_rate', 'gtd_rb_cost', 'dt_rf_cost', 'is_active')
    list_editable = ('is_active',)  # Редактирование активности
    ordering = ('-id',)  # Сортировка по ID


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone')  # Настройки сайта
    ordering = ('site_name',)  # Сортировка по названию

@admin.register(BannerImage)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')  # Баннеры
    search_fields = ('title', 'text')  # Поиск по заголовку и тексту
    fieldsets = (
        (None, {
            'fields': ('banner', 'title', 'text', 'is_active')
        }),
    )
    
    actions = ['activate_selected', 'deactivate_selected']  # Действия
    
    def activate_selected(self, request, queryset):
        # Активация только одного баннера
        if queryset.count() > 1:
            self.message_user(request, "Можно активировать только один баннер одновременно.", level='ERROR')
            return
        
        banner = queryset.first()
        banner.is_active = True
        banner.save()
        self.message_user(request, f"Активирован баннер: {banner.title}")
    
    activate_selected.short_description = "Активировать выбранный баннер (деактивирует другие)"
    
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {updated} баннеров")
    
    deactivate_selected.short_description = "Деактивировать выбранные баннеры"
    
    def save_model(self, request, obj, form, change):
        # Гарантия, что активен только один баннер
        if obj.is_active:
            BannerImage.objects.exclude(pk=obj.pk).filter(is_active=True).update(is_active=False)
        super().save_model(request, obj, form, change)
        
@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('name','symbol')  # Монеты/баллы

@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone')  # Офисы