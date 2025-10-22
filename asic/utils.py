from decimal import Decimal
from django.utils import timezone

def get_product_discounts(product, order_amount=Decimal('0')):
    """Mahsulotga tegishli barcha amaldagi chegirmalarni qaytaradi (faqat is_additional=False)"""
    from .models import Discount
    now = timezone.now()
    discounts = Discount.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now,
        min_order_amount__lte=order_amount,
        is_additional=False  # Faqat mahsulot uchun chegirmalar
    )
    
    # max_order_amount check qo'shish
    valid_discounts = []
    for discount in discounts:
        # Agar max_order_amount mavjud bo'lsa, tekshirish
        if hasattr(discount, 'max_order_amount') and discount.max_order_amount:
            if order_amount <= discount.max_order_amount and discount.is_valid_for_product(product):
                valid_discounts.append(discount)
        else:
            # Agar max_order_amount yo'q bo'lsa, oddiy tekshirish
            if discount.is_valid_for_product(product):
                valid_discounts.append(discount)
    
    return valid_discounts

def calculate_product_discount(product, price, order_amount=Decimal('0')):
    """
    Mahsulot uchun faqat is_additional=False chegirmalarni qo'llaydi.
    is_additional=True chegirmalar cart totalga qo'llanadi.
    """
    applicable_discounts = get_product_discounts(product, order_amount)

    if not applicable_discounts:
        return {
            'discounted_price': price,
            'total_discount': Decimal('0'),
            'total_discount_percent': Decimal('0'),
            'applied_discounts': []
        }

    # Faqat eng kuchli chegirmani qo'llaymiz
    applicable_discounts = sorted(applicable_discounts, key=lambda d: d.value, reverse=True)
    main_discount = applicable_discounts[0]

    final_price = Decimal(price)
    applied_discounts = []
    original_price = Decimal(price)

    if main_discount.discount_type == 'percentage':
        discount_amount = final_price * main_discount.value / Decimal('100')
        final_price -= discount_amount
        percent = main_discount.value
    else:  # fixed
        discount_amount = main_discount.value
        final_price = max(final_price - discount_amount, Decimal('0'))
        percent = (discount_amount / original_price * 100) if original_price > 0 else Decimal('0')

    applied_discounts.append({
        'discount': main_discount,
        'discount_amount': discount_amount.quantize(Decimal('0.01')),
        'discount_percent': percent.quantize(Decimal('0.01'))
    })

    total_discount = (original_price - final_price).quantize(Decimal('0.01'))
    total_percent = (total_discount / original_price * 100).quantize(Decimal('0.01')) if original_price > 0 else Decimal('0')

    return {
        'discounted_price': final_price.quantize(Decimal('0.01')),
        'total_discount': total_discount,
        'total_discount_percent': total_percent,
        'applied_discounts': applied_discounts
    }

def calculate_cart_total_discount(cart_total, user=None):
    """
    Savatdagi mahsulotlarning umumiy narxiga is_additional=True chegirmalarni qo'llash.
    Faqat min_order_amount va max_order_amount shartlariga mos keluvchi chegirmalar qo'llanadi.
    """
    from .models import Discount
    from django.utils import timezone
    
    now = timezone.now()
    additional_discounts = Discount.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now,
        min_order_amount__lte=cart_total,
        is_additional=True,
        apply_to='all'
    ).order_by('-value')
    
    # max_order_amount filterlash
    valid_discounts = []
    for discount in additional_discounts:
        if hasattr(discount, 'max_order_amount') and discount.max_order_amount:
            if cart_total <= discount.max_order_amount:
                valid_discounts.append(discount)
        else:
            # Agar max_order_amount yo'q bo'lsa, oddiy qo'shish
            valid_discounts.append(discount)
    
    if not valid_discounts:
        return {
            'final_cart_total': cart_total,
            'cart_discount': Decimal('0'),
            'cart_discount_percent': Decimal('0'),
            'applied_cart_discounts': []
        }
    
    final_total = cart_total
    total_cart_discount = Decimal('0')
    applied_cart_discounts = []
    
    # Eng katta chegirmani qo'llash (bitta chegirma)
    main_discount = valid_discounts[0]
    
    if main_discount.discount_type == 'percentage':
        discount_amount = final_total * main_discount.value / Decimal('100')
        final_total -= discount_amount
        percent = main_discount.value
    else:  # fixed
        discount_amount = min(main_discount.value, final_total)
        final_total -= discount_amount
        percent = (discount_amount / cart_total * 100) if cart_total > 0 else Decimal('0')
    
    total_cart_discount += discount_amount
    
    applied_cart_discounts.append({
        'discount': main_discount,
        'discount_name': main_discount.name,
        'discount_type': main_discount.discount_type,
        'discount_amount': discount_amount.quantize(Decimal('0.01')),
        'discount_percent': percent.quantize(Decimal('0.01')),
        'is_first_order': False
    })
    
    total_cart_percent = (total_cart_discount / cart_total * 100).quantize(Decimal('0.01')) if cart_total > 0 else Decimal('0')
    
    return {
        'final_cart_total': max(final_total.quantize(Decimal('0.01')), Decimal('0')),
        'cart_discount': total_cart_discount.quantize(Decimal('0.01')),
        'cart_discount_percent': total_cart_percent,
        'applied_cart_discounts': applied_cart_discounts
    }
