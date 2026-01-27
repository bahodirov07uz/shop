from django.contrib import admin
from .models import (
    Manufacturer, ProductCategory, Product,
    Order, OrderStatusHistory, Discount,
    DeliverySettings, SiteSettings, OrderItem, 
    BannerImage, Coin, Office, StaticPage, 
    Cards, TemplateEdit, About_page, PayCheck, 
    Privacy, Profile, OrderStatusRule, AboutStat
)
from import_export.admin import ImportExportModelAdmin
from .resources import ProductResource

# ===== ISHLAB CHIQARUVCHILAR =====
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)
    
    class Meta:
        verbose_name = 'Ishlab chiqaruvchi'
        verbose_name_plural = 'Ishlab chiqaruvchilar'


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
    fieldsets = (
        (None, {
            "fields": (
                ("title", "main_text"),
                ("courier_title", "air_title", "sea_title"),
                ("free_shipping_text", "paid_shipping_text"),
                ("important_info_title", "important_info_body"),
            )
        }),
    )
    search_fields = ("title", "courier_title", "air_title", "sea_title")
    ordering = ("-updated_at",)


# ===== MAHSULOT KATEGORIYALARI =====
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('parent',)
    ordering = ('name',)
    
    class Meta:
        verbose_name = 'Mahsulot kategoriyasi'
        verbose_name_plural = 'Mahsulot kategoriyalari'

# ===== MAHSULOTLAR =====
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
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'

# ===== BUYURTMALAR =====
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    class Meta:
        verbose_name = 'Buyurtma pozitsiyasi'
        verbose_name_plural = 'Buyurtma pozitsiyalari'

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
               'set_status_ready', 'set_status_completed', 'set_status_cancelled']

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Mahsulotlar soni'

    def items_list(self, obj):
        return ", ".join([f"{item.product.name} ({item.quantity})" for item in obj.items.all()])
    items_list.short_description = 'Buyurtma tarkibi'

    # === OMMAVIY AMALLAR ===
    def set_status_new(self, request, queryset):
        queryset.update(status='new')
    set_status_new.short_description = "Holatni o'zgartirish: Yangi buyurtma"

    def set_status_processing(self, request, queryset):
        queryset.update(status='processing')
    set_status_processing.short_description = "Holatni o'zgartirish: Ishlov berilmoqda"

    def set_status_shipped(self, request, queryset):
        queryset.update(status='shipped')
    set_status_shipped.short_description = "Holatni o'zgartirish: Yuborildi"

    def set_status_ready(self, request, queryset):
        queryset.update(status='ready')
    set_status_ready.short_description = "Holatni o'zgartirish: Yuborishga tayyor"

    def set_status_completed(self, request, queryset):
        queryset.update(status='completed')
    set_status_completed.short_description = "Holatni o'zgartirish: Yakunlandi"

    def set_status_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    set_status_cancelled.short_description = "Holatni o'zgartirish: Bekor qilindi"


from .models import OrderStatusRule

@admin.register(OrderStatusRule)
class OrderStatusRuleAdmin(admin.ModelAdmin):
    list_display = ("status", "days_after", 'order_priority', "is_active")
    list_editable = ("days_after", 'order_priority', "is_active")
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
    order_status.short_description = 'Buyurtma holati'
    
    class Meta:
        verbose_name = 'Buyurtma pozitsiyasi'
        verbose_name_plural = 'Buyurtma pozitsiyalari'

# ===== BUYURTMA HOLATLARI TARIXI =====
@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('order__order_number',)
    autocomplete_fields = ('order',)
    
    class Meta:
        verbose_name = 'Buyurtma holati tarixi'
        verbose_name_plural = 'Buyurtma holatlari tarixi'

# ===== CHEGIRMALAR =====

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
    list_editable = ('value', 'min_order_amount', 'max_order_amount', 'is_active', 'is_additional')
    
    search_fields = ('name',)
    filter_horizontal = ('categories', 'products', 'manufacturers')
    readonly_fields = ('created_at',)
    ordering = ('-id',)

    class Meta:
        verbose_name = 'Chegirma'
        verbose_name_plural = 'Chegirmalar'


# ===== YETKAZIB BERISH SOZLAMALARI =====
@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ('air_delivery_rate', 'sea_delivery_rate', 'gtd_rb_cost', 'dt_rf_cost', 'is_active')
    list_editable = ('is_active',)
    ordering = ('-id',)
    
    class Meta:
        verbose_name = 'Yetkazib berish sozlamasi'
        verbose_name_plural = 'Yetkazib berish sozlamalari'

# ===== SAYT SOZLAMALARI =====
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone', 'telegram', 'whatsapp', 'vkontakte')
    ordering = ('site_name',)
    
    class Meta:
        verbose_name = 'Sayt sozlamasi'
        verbose_name_plural = 'Sayt sozlamalari'

# ===== FOYDALANUVCHI PROFILLARI =====
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
        verbose_name = 'Profil'
        verbose_name_plural = 'Profillar'

# ===== OFISLAR =====
@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone', 'email', 'telegram', 'whatsapp', 'vkontakte')
    list_filter = ('name',)
    search_fields = ('name', 'location', 'phone')
    
    class Meta:
        verbose_name = 'Ofis'
        verbose_name_plural = 'Ofislar'

# ===== BANNERLAR =====
@admin.register(BannerImage)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title', 'text')
    
    actions = ['activate_selected', 'deactivate_selected']
    
    def activate_selected(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, "Bir vaqtning o'zida faqat bitta bannerni faollashtirish mumkin.", level='ERROR')
            return
        
        banner = queryset.first()
        banner.is_active = True
        banner.save()
        self.message_user(request, f"Faollashtirildi: {banner.title}")
    
    activate_selected.short_description = "Tanlangan bannerni faollashtirish"
    
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} ta banner o'chirildi")
    
    deactivate_selected.short_description = "Tanlangan bannerlarni o'chirish"
    
    def save_model(self, request, obj, form, change):
        if obj.is_active:
            BannerImage.objects.exclude(pk=obj.pk).filter(is_active=True).update(is_active=False)
        super().save_model(request, obj, form, change)
    
    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Bannerlar'

# ===== TANGALAR =====
@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    
    class Meta:
        verbose_name = 'Tanga'
        verbose_name_plural = 'Tangalar'

# ===== STATIK SAHIFALAR =====
@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'slug')
    
    class Meta:
        verbose_name = 'Statik sahifa'
        verbose_name_plural = 'Statik sahifalar'

# ===== KARTALAR =====
@admin.register(Cards)
class CardsAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "icon", "is_about")
    list_filter = ("is_about",)
    search_fields = ("title", "text")
    
    class Meta:
        verbose_name = 'Karta'
        verbose_name_plural = 'Kartalar'

# ===== "BIZ HAQIMIZDA" SAHIFASI =====
@admin.register(About_page)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('about_title', 'benefit_title')
    filter_horizontal = ('statistics',)
    
    class Meta:
        verbose_name = '"Biz haqimizda" sahifasi'
        verbose_name_plural = '"Biz haqimizda" sahifalari'

# ===== TO'LOV VA YETKAZIB BERISH =====
@admin.register(PayCheck)
class PayCheckAdmin(admin.ModelAdmin):
    list_display = ("id",)
    
    class Meta:
        verbose_name = "To'lov va yetkazib berish"
        verbose_name_plural = "To'lov va yetkazib berish"

# ===== MAXFIYLIK SIYOSATI =====
@admin.register(Privacy)
class PrivacyAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title", "text")
    
    class Meta:
        verbose_name = 'Maxfiylik siyosati'
        verbose_name_plural = 'Maxfiylik siyosati'

# ===== BIZ HAQIMIZDA STATISTIKA =====
@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    list_display = ("number", "text")
    search_fields = ("number", "text")
    
    class Meta:
        verbose_name = 'Biz haqimizda statistika'
        verbose_name_plural = 'Biz haqimizda statistika'


from .models import PageTitle

@admin.register(PageTitle)
class PageTitleAdmin(admin.ModelAdmin):
    list_display = ['id']


# Model nomlarini o'zbek tiliga o'zgartirish
Manufacturer._meta.verbose_name = 'Ishlab chiqaruvchi'
Manufacturer._meta.verbose_name_plural = 'Ishlab chiqaruvchilar'

ProductCategory._meta.verbose_name = 'Mahsulot kategoriyasi'
ProductCategory._meta.verbose_name_plural = 'Mahsulot kategoriyalari'

Product._meta.verbose_name = 'Mahsulot'
Product._meta.verbose_name_plural = 'Mahsulotlar'

Order._meta.verbose_name = 'Buyurtma'
Order._meta.verbose_name_plural = 'Buyurtmalar'

OrderItem._meta.verbose_name = 'Buyurtma pozitsiyasi'
OrderItem._meta.verbose_name_plural = 'Buyurtma pozitsiyalari'

OrderStatusHistory._meta.verbose_name = 'Buyurtma holati tarixi'
OrderStatusHistory._meta.verbose_name_plural = 'Buyurtma holatlari tarixi'

Discount._meta.verbose_name = 'Chegirma'
Discount._meta.verbose_name_plural = 'Chegirmalar'

DeliverySettings._meta.verbose_name = 'Yetkazib berish sozlamasi'
DeliverySettings._meta.verbose_name_plural = 'Yetkazib berish sozlamalari'

SiteSettings._meta.verbose_name = 'Sayt sozlamasi'
SiteSettings._meta.verbose_name_plural = 'Sayt sozlamalari'

Profile._meta.verbose_name = 'Profil'
Profile._meta.verbose_name_plural = 'Profillar'

BannerImage._meta.verbose_name = 'Banner'
BannerImage._meta.verbose_name_plural = 'Bannerlar'

Coin._meta.verbose_name = 'Tanga'
Coin._meta.verbose_name_plural = 'Tangalar'

Office._meta.verbose_name = 'Ofis'
Office._meta.verbose_name_plural = 'Ofislar'

StaticPage._meta.verbose_name = 'Statik sahifa'
StaticPage._meta.verbose_name_plural = 'Statik sahifalar'

Cards._meta.verbose_name = 'Karta'
Cards._meta.verbose_name_plural = 'Kartalar'

About_page._meta.verbose_name = '"Biz haqimizda" sahifasi'
About_page._meta.verbose_name_plural = '"Biz haqimizda" sahifalari'

PayCheck._meta.verbose_name = "To'lov va yetkazib berish"
PayCheck._meta.verbose_name_plural = "To'lov va yetkazib berish"

Privacy._meta.verbose_name = 'Maxfiylik siyosati'
Privacy._meta.verbose_name_plural = 'Maxfiylik siyosati'

AboutStat._meta.verbose_name = 'Biz haqimizda statistika'
AboutStat._meta.verbose_name_plural = 'Biz haqimizda statistika'