from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from asic.models import Product, Manufacturer, ProductCategory
from django.utils.text import slugify
import requests
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import os
import time
from import_export import widgets

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
        fields = (
            'name', 'slug', 'manufacturer', 'category', 'price', 'old_price',
            'description', 'specifications', 'images', 'image2', 'image3',
            'variant_colors', 'variant_sizes', 'default_variant_stock',
            'is_featured', 'is_active', 'meta_title', 'meta_description'
        )

    def before_import_row(self, row, **kwargs):
        if 'slug' not in row or not row['slug']:
            row['slug'] = slugify(row['name'])

    def save_instance(self, instance, is_create, using_transactions=True, dry_run=False):
        for field_name in ['images', 'image2', 'image3']:
            value = getattr(instance, field_name, None)
            if value and isinstance(value, tuple):
                content, filename = value
                getattr(instance, field_name).save(filename, content, save=False)

        super().save_instance(instance, is_create, using_transactions=using_transactions, dry_run=dry_run)
