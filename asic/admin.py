from django.contrib import admin
from .models import (
    Manufacturer, ProductCategory, Product,
     Order, OrderStatusHistory, Discount,
    DeliverySettings, SiteSettings,OrderItem,BannerImage,Coin,Office
)
from import_export.admin import ExportMixin
from .resources import ProductResource

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('parent',)
    ordering = ('name',)


from import_export.admin import ImportExportModelAdmin

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):  # ✅ to‘g‘risi shu
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


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at', 'items_count')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'order_number', 'items_list')
    autocomplete_fields = ('user',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    actions = ['mark_as_completed', 'mark_as_shipped', 'mark_as_customs']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'delivery_cost', 'document_cost', 'total')
        }),
        ('Delivery Information', {
            'fields': ('delivery_type', 'document_type', 'shipping_address', 'billing_address')
        }),
        ('Additional Information', {
            'fields': ('payment_status', 'notes', 'created_at', 'updated_at')
        }),
    )
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'

    def items_list(self, obj):
        return ", ".join([f"{item.product.name} ({item.quantity})" for item in obj.items.all()])
    items_list.short_description = 'Order Items'

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
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name')
    raw_id_fields = ('order', 'product')
    
    def order_status(self, obj):
        return obj.order.status
    order_status.short_description = 'Order Status'
    order_status.admin_order_field = 'order__status'
@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('order__order_number',)
    autocomplete_fields = ('order',)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'value', 'apply_to', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'discount_type', 'apply_to')
    search_fields = ('name',)
    filter_horizontal = ('categories', 'products', 'manufacturers')
    readonly_fields = ('created_at',)
    ordering = ('-start_date',)


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ('air_delivery_rate', 'sea_delivery_rate', 'gtd_rb_cost', 'dt_rf_cost', 'is_active')
    list_editable = ('is_active',)
    ordering = ('-id',)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone')
    ordering = ('site_name',)

from django.contrib import admin
from .models import BannerImage

@admin.register(BannerImage)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title', 'text')
    fieldsets = (
        (None, {
            'fields': ('banner', 'title', 'text', 'is_active')
        }),
    )
    
    actions = ['activate_selected', 'deactivate_selected']
    
    def activate_selected(self, request, queryset):
        # Only activate one banner at a time
        if queryset.count() > 1:
            self.message_user(request, "You can only activate one banner at a time.", level='ERROR')
            return
        
        banner = queryset.first()
        banner.is_active = True
        banner.save()
        self.message_user(request, f"Activated banner: {banner.title}")
    
    activate_selected.short_description = "Activate selected banner (deactivates others)"
    
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} banners")
    
    deactivate_selected.short_description = "Deactivate selected banners"
    
    def save_model(self, request, obj, form, change):
        # Ensure only one active banner exists
        if obj.is_active:
            BannerImage.objects.exclude(pk=obj.pk).filter(is_active=True).update(is_active=False)
        super().save_model(request, obj, form, change)
        
admin.site.register(Coin)

@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone')
