from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (
    Manufacturer,
    ProductCategory,
    Size,
    Product,
    ProductVariant,
    Order,
    OrderItem,
    OrderStatusHistory,
    Discount,
    DeliverySettings,
    SiteSettings,
    BannerImage,
    Office,
    StaticPage,
    Cards,
    About_page,
    PayCheck,
    Privacy,
    Profile,
    OrderStatusRule,
    AboutStat,
    PageTitle,
    DeliveryInfo,
)
from .resources import ProductResource


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name",)
    list_filter = ("is_active",)
    ordering = ("name",)


@admin.register(DeliveryInfo)
class DeliveryInfoAdmin(admin.ModelAdmin):
    list_display = ("title", "courier_title", "air_title", "sea_title", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("title", "main_text"),
                    ("courier_title", "air_title", "sea_title"),
                    ("free_shipping_text", "paid_shipping_text"),
                    ("important_info_title", "important_info_body"),
                )
            },
        ),
    )
    search_fields = ("title", "courier_title", "air_title", "sea_title")
    ordering = ("-updated_at",)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("parent",)
    ordering = ("name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    list_editable = ("sort_order",)
    search_fields = ("name",)
    ordering = ("sort_order", "name")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("color", "size", "image", "sku", "stock", "is_active")
    readonly_fields = ("sku",)


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ("name", "manufacturer", "category", "price", "stock", "is_active")
    list_editable = ("price", "is_active")
    list_filter = ("is_active", "is_featured", "category", "manufacturer")
    search_fields = ("name", "description", "specifications")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "stock")
    autocomplete_fields = ("manufacturer", "category")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    inlines = [ProductVariantInline]

    fieldsets = (
        (
            "Asosiy",
            {
                "fields": (
                    "name",
                    "slug",
                    ("manufacturer", "category"),
                    ("price", "old_price"),
                    ("images", "image2", "image3"),
                    ("is_featured", "is_active"),
                )
            },
        ),
        (
            "Tavsif",
            {"fields": ("description", "specifications")},
        ),
        (
            "Variant sozlamalari",
            {"fields": ("variant_colors", "variant_sizes", "sizes", "default_variant_stock", "stock")},
        ),
        (
            "SEO",
            {"fields": ("meta_title", "meta_description")},
        ),
        (
            "Sana",
            {"fields": ("created_at", "updated_at")},
        ),
    )

    actions = ["generate_variants"]

    def generate_variants(self, request, queryset):
        for product in queryset:
            product.generate_variants()
    generate_variants.short_description = "Variantlarni qayta yaratish"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "color", "size", "stock", "is_active")
    list_filter = ("is_active", "color", "size", "product__manufacturer")
    search_fields = ("sku", "product__name", "color", "size")
    autocomplete_fields = ("product",)
    ordering = ("product", "color", "size")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "variant", "price", "quantity")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "total", "created_at", "items_count")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "user__username")
    readonly_fields = ("created_at", "updated_at", "items_list")
    autocomplete_fields = ("user",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    actions = [
        "set_status_new",
        "set_status_processing",
        "set_status_shipped",
        "set_status_ready",
        "set_status_completed",
        "set_status_cancelled",
    ]

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Pozitsiyalar soni"

    def items_list(self, obj):
        return ", ".join(
            [
                f"{item.product.name} ({item.quantity})"
                for item in obj.items.all()
            ]
        )
    items_list.short_description = "Buyurtma tarkibi"

    def set_status_new(self, request, queryset):
        queryset.update(status="new")
    set_status_new.short_description = "Holat: Yangi"

    def set_status_processing(self, request, queryset):
        queryset.update(status="processing")
    set_status_processing.short_description = "Holat: Jarayonda"

    def set_status_shipped(self, request, queryset):
        queryset.update(status="shipped")
    set_status_shipped.short_description = "Holat: Yuborildi"

    def set_status_ready(self, request, queryset):
        queryset.update(status="pickup_ready")
    set_status_ready.short_description = "Holat: Olib ketishga tayyor"

    def set_status_completed(self, request, queryset):
        queryset.update(status="completed")
    set_status_completed.short_description = "Holat: Yakunlandi"

    def set_status_cancelled(self, request, queryset):
        queryset.update(status="cancelled")
    set_status_cancelled.short_description = "Holat: Bekor qilindi"


@admin.register(OrderStatusRule)
class OrderStatusRuleAdmin(admin.ModelAdmin):
    list_display = ("status", "days_after", "order_priority", "is_active")
    list_editable = ("days_after", "order_priority", "is_active")
    ordering = ("days_after",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "variant", "price", "quantity", "order_status")
    list_filter = ("order__status",)
    search_fields = ("order__order_number", "product__name", "variant__sku")
    raw_id_fields = ("order", "product", "variant")

    def order_status(self, obj):
        return obj.order.status
    order_status.short_description = "Buyurtma holati"


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("order__order_number",)
    autocomplete_fields = ("order",)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "value",
        "min_order_amount",
        "max_order_amount",
        "is_active",
        "is_additional",
    )
    list_editable = ("value", "min_order_amount", "max_order_amount", "is_active", "is_additional")
    search_fields = ("name",)
    filter_horizontal = ("categories", "products", "manufacturers")
    readonly_fields = ("created_at",)
    ordering = ("-id",)


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ("air_delivery_rate", "sea_delivery_rate", "gtd_rb_cost", "dt_rf_cost", "is_active")
    list_editable = ("is_active",)
    ordering = ("-id",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "email", "phone", "telegram", "whatsapp", "vkontakte")
    ordering = ("site_name",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "name", "email")
    search_fields = ("user__username", "phone", "name", "user__email")
    raw_id_fields = ("user",)
    list_filter = ("user__is_active",)

    def email(self, obj):
        return obj.user.email
    email.short_description = "Email"


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "phone", "email", "telegram", "whatsapp", "vkontakte")
    list_filter = ("name",)
    search_fields = ("name", "location", "phone")


@admin.register(BannerImage)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")
    search_fields = ("title", "text")
    actions = ["activate_selected", "deactivate_selected"]

    def activate_selected(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                "Bir vaqtning o'zida faqat bitta bannerni faollashtirish mumkin.",
                level="ERROR",
            )
            return

        banner = queryset.first()
        banner.is_active = True
        banner.save()
        self.message_user(request, f"Faollashtirildi: {banner.title}")
    activate_selected.short_description = "Tanlangan bannerni faollashtirish"

    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} ta banner ochirildi")
    deactivate_selected.short_description = "Tanlangan bannerlarni ochirish"

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            BannerImage.objects.exclude(pk=obj.pk).filter(is_active=True).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ("slug", "title")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")


@admin.register(Cards)
class CardsAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "icon", "is_about")
    list_filter = ("is_about",)
    search_fields = ("title", "text")


@admin.register(About_page)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ("about_title", "benefit_title")
    filter_horizontal = ("statistics",)


@admin.register(PayCheck)
class PayCheckAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Privacy)
class PrivacyAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title", "text")


@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    list_display = ("number", "text")
    search_fields = ("number", "text")


@admin.register(PageTitle)
class PageTitleAdmin(admin.ModelAdmin):
    list_display = ["id"]
