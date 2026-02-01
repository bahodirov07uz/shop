# asic/cart.py

from django.conf import settings
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart_key = getattr(settings, 'CART_SESSION_ID', 'cart')
        cart = self.session.get(self.cart_key)
        if not cart:
            cart = self.session[self.cart_key] = {}
        self.cart = cart

    def add(self, variant, quantity=1, update_quantity=False):
        """Variantni savatga qo'shish"""
        variant_id = str(variant.id)
        if variant_id not in self.cart:
            self.cart[variant_id] = {
                'quantity': 0,
                'price': str(variant.product.current_price)
            }
        if update_quantity:
            self.cart[variant_id]['quantity'] = quantity
        else:
            self.cart[variant_id]['quantity'] += quantity
        self.save()

    def remove(self, variant):
        variant_id = str(variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def is_variant_in_cart(self, variant_id):
        """Variant kartada borligini tekshirish"""
        return str(variant_id) in self.cart

    def is_product_in_cart(self, product_id):
        """Orqaga moslik uchun"""
        return self.is_variant_in_cart(product_id)

    def get_variant_quantity(self, variant_id):
        """Variantning kartadagi miqdorini olish"""
        variant_id = str(variant_id)
        return self.cart.get(variant_id, {}).get('quantity', 0)

    def get_product_quantity(self, product_id):
        """Orqaga moslik uchun"""
        return self.get_variant_quantity(product_id)

    def save(self):
        """Session ni saqlash"""
        self.session.modified = True
        self.session.save()  # Явно сохраняем session
        logger.debug(f"Cart saved. Session key: {self.session.session_key}")

    def __iter__(self):
        """Cart ichidagi itemlarni iteratsiya qilish"""
        try:
            ProductVariant = apps.get_model('asic', 'ProductVariant')
        except LookupError:
            return iter([])

        # faqat raqamli ID larni olish
        variant_ids = []
        for vid in self.cart.keys():
            if str(vid).isdigit():
                variant_ids.append(int(vid))

        if not variant_ids:
            return iter([])

        variants = ProductVariant.objects.filter(id__in=variant_ids).select_related("product", "product__manufacturer")
        variants_dict = {str(v.id): v for v in variants}

        cart = self.cart.copy()

        for variant_id, item in cart.items():
            if variant_id in variants_dict:
                variant = variants_dict[variant_id]
                product = variant.product
                if product:
                    item['variant'] = variant
                    item['product'] = product
                    item['price'] = float(product.current_price)
                    item['stock'] = variant.stock
                    item['total_price'] = item['price'] * item['quantity']
                    yield item

    def __len__(self):
        """Cartdagi jami mahsulotlar soni"""
        return sum(item['quantity'] for item in self.cart.values() if isinstance(item.get('quantity'), int))

    def get_total_price(self):
        """Savat umumiy narxi"""
        total = 0
        try:
            for item in self:
                total += item['total_price']
        except Exception:
            pass
        return total

    def clear(self):
        """Cartni to'liq tozalash"""
        logger.info(f"🧹 Clearing cart. Session key: {self.session.session_key}")
        logger.info(f"🧹 Cart items before clear: {len(self.cart)}")
        
        # Session dan cart ni o'chirish
        if self.cart_key in self.session:
            del self.session[self.cart_key]
            self.session.modified = True
            self.session.save()  # Явно сохраняем
            logger.info(f"✅ Cart cleared successfully")
        
        # Local cart ni ham tozalash
        self.cart = {}
        
        # Проверка
        if self.cart_key in self.session:
            logger.warning(f"⚠️ Cart still exists in session after clear!")
        else:
            logger.info(f"✅ Verified: cart removed from session")

    def clean_invalid_items(self):
        """Yaroqsiz itemlarni tozalash"""
        ProductVariant = apps.get_model('asic', 'ProductVariant')
        valid_ids = list(ProductVariant.objects.values_list('id', flat=True))
        valid_ids_str = [str(id) for id in valid_ids]

        items_to_remove = []
        for variant_id in list(self.cart.keys()):
            if variant_id not in valid_ids_str:
                items_to_remove.append(variant_id)

        for variant_id in items_to_remove:
            del self.cart[variant_id]

        if items_to_remove:
            self.save()
            logger.info(f"🧹 Removed {len(items_to_remove)} invalid items from cart")
