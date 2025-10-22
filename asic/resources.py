from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from asic.models import Product, Manufacturer, ProductCategory, Coin
from django.utils.text import slugify
import requests
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import os
from import_export import widgets  # Import the widgets module

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


class ManufacturerOrCreateWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        try:
            return self.get_queryset(value, row, *args, **kwargs).get(**{self.field: value})
        except self.model.DoesNotExist:
            return self.model.objects.create(**{self.field: value})


from import_export import widgets

class HashUnitWidget(widgets.Widget):
    MAPPING = {
        'TH/s': 'TH',
        'GH/s': 'GH',
        'MH/s': 'MH',
        'TH': 'TH',
        'GH': 'GH',
        'MH': 'MH',
    }

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        value = value.strip()
        if value not in self.MAPPING:
            raise ValueError(f"Invalid hash_unit value: {value}")
        return self.MAPPING[value]


class ImageURLWidget(widgets.Widget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        
        try:
            response = requests.get(value, stream=True)
            response.raise_for_status()
            
            # Extract filename from URL
            parsed_url = urlparse(value)
            filename = os.path.basename(parsed_url.path)
            if not filename:  # If URL doesn't contain filename
                filename = f"image_{int(time.time())}.jpg"
            
            # Create ContentFile and set name attribute
            image_content = ContentFile(response.content)
            image_content.name = filename
            
            return image_content
        except Exception as e:
            print(f"Error downloading image from {value}: {e}")
            return None

    def save_instance(self, instance, is_create, using_transactions=True, dry_run=False):
        # First save the instance without the images to get a PK
        super().save_instance(instance, is_create, using_transactions=using_transactions, dry_run=dry_run)
        
        # Then handle the image fields if this is not a dry run
        if not dry_run:
            for field_name in ['images', 'image2', 'image3']:
                field = getattr(instance, field_name)
                if field and isinstance(field, ContentFile):
                    # Save the image file properly
                    getattr(instance, field_name).save(field.name, field, save=True)
                    
                    
class ProductResource(resources.ModelResource):
    hash_unit = fields.Field(
        column_name='hash_unit',
        attribute='hash_unit',
        widget=HashUnitWidget()
    )
    
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
    images = fields.Field(
        column_name='images',
        attribute='images',
        widget=ImageURLWidget()
    )
    image2 = fields.Field(
        column_name='image2',
        attribute='image2',
        widget=ImageURLWidget()
    )
    image3 = fields.Field(
        column_name='image3',
        attribute='image3',
        widget=ImageURLWidget()
    )

    class Meta:
        model = Product
        import_id_fields = ['slug']
        skip_unchanged = True
        report_skipped = True
        fields = ('name', 'slug', 'manufacturer', 'category', 'price', 'old_price',
                 'hash_rate', 'power_consumption', 'algorithm', 'description',
                 'specifications', 'images', 'image2', 'image3', 'stock',
                 'is_featured', 'is_active', 'coins')

    def before_import_row(self, row, **kwargs):
        # Ensure slug is created if not provided
        if 'slug' not in row or not row['slug']:
            row['slug'] = slugify(row['name'])

    def save_instance(self, instance, is_create, using_transactions=True, dry_run=False):
        for field_name in ['images', 'image2', 'image3']:
            value = getattr(instance, field_name, None)
            if value and isinstance(value, tuple):
                content, filename = value
                getattr(instance, field_name).save(filename, content, save=False)

        super().save_instance(instance, is_create, using_transactions=using_transactions, dry_run=dry_run)
