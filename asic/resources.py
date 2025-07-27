from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from asic.models import Product, Manufacturer, ProductCategory, Coin
from django.utils.text import slugify

class ProductCategoryOrCreateWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        try:
            return self.get_queryset(value, row, *args, **kwargs).get(**{self.field: value})
        except self.model.DoesNotExist:
            # Slug yaratish va mavjudligini tekshirish
            base_slug = slugify(value)
            slug = base_slug
            i = 1
            while self.model.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            return self.model.objects.create(**{self.field: value, 'slug': slug})


# Manufacturerni avtomatik yaratish
class ManufacturerOrCreateWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        try:
            return self.get_queryset(value, row, *args, **kwargs).get(**{self.field: value})
        except self.model.DoesNotExist:
            return self.model.objects.create(**{self.field: value})

class ProductCategoryOrCreateWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        try:
            return self.get_queryset(value, row, *args, **kwargs).get(**{self.field: value})
        except self.model.DoesNotExist:
            # Slug yaratish va mavjudligini tekshirish
            base_slug = slugify(value)
            slug = base_slug
            i = 1
            while self.model.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            return self.model.objects.create(**{self.field: value, 'slug': slug})

# Asosiy Product resource
class ProductResource(resources.ModelResource):
    manufacturer = fields.Field(
        column_name='manufacturer',
        attribute='manufacturer',
        widget=ManufacturerOrCreateWidget(Manufacturer, 'name')
    )
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ProductCategoryOrCreateWidget(ProductCategory, 'name')
    )
    coins = fields.Field(
        column_name='coins',
        attribute='coins',
        widget=ManyToManyWidget(Coin, field='name', separator=',')
    )

    class Meta:
        model = Product
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True
