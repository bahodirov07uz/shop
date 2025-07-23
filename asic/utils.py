from decimal import Decimal
from django.utils import timezone

def get_product_discounts(product, order_amount=Decimal('0')):
    """Mahsulotga tegishli barcha amaldagi chegirmalarni qaytaradi"""
    from .models import Discount
    now = timezone.now()
    discounts = Discount.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now,
        min_order_amount__lte=order_amount
    )
    
    return [d for d in discounts if d.is_valid_for_product(product)]

def calculate_product_discount(product, price, order_amount=Decimal('0')):
    """Mahsulot uchun eng yaxshi chegirmani hisoblaydi"""
    from .models import Discount

    applicable_discounts = get_product_discounts(product, order_amount)
    if not applicable_discounts:
        return {
            'discounted_price': price,
            'discount_amount': Decimal('0'),
            'discount_percent': Decimal('0'),
            'discount': None
        }
    
    # Eng yuqori chegirmani tanlash
    best_discount = max(applicable_discounts, key=lambda d: d.value)
    
    if best_discount.discount_type == 'percentage':
        discount_amount = price * best_discount.value / Decimal('100')
        discounted_price = price - discount_amount
        discount_percent = best_discount.value
    else:
        discount_amount = best_discount.value
        discounted_price = max(price - discount_amount, Decimal('0'))
        discount_percent = (discount_amount / price * 100) if price > 0 else Decimal('0')
    
    return {
        'discounted_price': discounted_price.quantize(Decimal('0.01')),
        'discount_amount': discount_amount.quantize(Decimal('0.01')),
        'discount_percent': discount_percent.quantize(Decimal('0.01')),
        'discount': best_discount
    }