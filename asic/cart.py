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

    def add(self, product, quantity=1, update_quantity=False):
        """Mahsulotni savatga qo'shish"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.current_price)
            }
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def is_product_in_cart(self, product_id):
        """Mahsulot kartada borligini tekshirish"""
        return str(product_id) in self.cart

    def get_product_quantity(self, product_id):
        """Mahsulotning kartadagi miqdorini olish"""
        product_id = str(product_id)
        return self.cart.get(product_id, {}).get('quantity', 0)

    def save(self):
        """Session ni saqlash"""
        self.session.modified = True
        self.session.save()  # Явно сохраняем session
        logger.debug(f"Cart saved. Session key: {self.session.session_key}")

    def __iter__(self):
        """Cart ichidagi itemlarni iteratsiya qilish"""
        try:
            Product = apps.get_model('asic', 'Product')
        except LookupError:
            return iter([])

        # faqat raqamli ID larni olish
        product_ids = []
        for pid in self.cart.keys():
            if str(pid).isdigit():
                product_ids.append(int(pid))

        if not product_ids:
            return iter([])

        products = Product.objects.filter(id__in=product_ids).select_related()
        products_dict = {str(p.id): p for p in products}

        cart = self.cart.copy()

        for product_id, item in cart.items():
            if product_id in products_dict:
                product = products_dict[product_id]
                if product:
                    item['product'] = product
                    item['price'] = float(product.current_price)
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
        Product = apps.get_model('asic', 'Product')
        valid_ids = list(Product.objects.values_list('id', flat=True))
        valid_ids_str = [str(id) for id in valid_ids]

        items_to_remove = []
        for product_id in list(self.cart.keys()):
            if product_id not in valid_ids_str:
                items_to_remove.append(product_id)

        for product_id in items_to_remove:
            del self.cart[product_id]

        if items_to_remove:
            self.save()
            logger.info(f"🧹 Removed {len(items_to_remove)} invalid items from cart")
