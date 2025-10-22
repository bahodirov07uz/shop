import uuid
from django.db import transaction
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView,DetailView,ListView
from .models import Product,Manufacturer,Order,OrderItem,DeliverySettings,BannerImage,Profile,Office,StaticPage,PayCheck,About_page,Privacy,Discount
from django.core.paginator import Paginator
from .cart import Cart
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal,InvalidOperation
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_POST
from payments.models import Payment
import requests
from django.db.models import Max,Min,Count
from .utils import calculate_product_discount,calculate_cart_total_discount

class HomeView(ListView):
    template_name = "index.html"
    model = Product
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        active_banner = BannerImage.objects.filter(is_active=True).first()
        context['products'] = Product.objects.all()[:3]
        context['partners'] = Manufacturer.objects.filter(is_active=True)[:8]
        context['active_banner'] = active_banner

        return context

from django.views.generic import ListView
from django.db.models import Q
from .models import Product, Manufacturer, Coin

from django.db.models import Min, Max, Q, Count
from django.views.generic import ListView
from .models import Product, Manufacturer, Coin

from django.db.models import Min, Max, Count, Q
from django.conf import settings

class CatalogView(ListView):
    template_name = "catalog.html"
    model = Product
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('manufacturer')

        # Parametrlarni olish
        manufacturers = self.request.GET.getlist("manufacturer")
        algorithms = self.request.GET.getlist("algorithm")
        coins = self.request.GET.getlist("coin")
        price_from = self.request.GET.get("price_from")
        price_to = self.request.GET.get("price_to")
        in_stock = self.request.GET.get("in_stock")
        sort = self.request.GET.get("sort")

        # Yangi filtrlar
        min_hashrate = self.request.GET.get("min_hashrate")
        max_hashrate = self.request.GET.get("max_hashrate")
        min_power = self.request.GET.get("min_power")
        max_power = self.request.GET.get("max_power")

        # Filtrlarni qo'llash
        if manufacturers:
            # String yoki int qiymatlarni handle qilish
            manufacturer_ids = []
            for m in manufacturers:
                try:
                    manufacturer_ids.append(int(m))
                except (ValueError, TypeError):
                    pass
            if manufacturer_ids:
                queryset = queryset.filter(manufacturer__id__in=manufacturer_ids)

        if algorithms:
            # Bo'sh qiymatlarni filtrlash
            valid_algorithms = [a for a in algorithms if a.strip()]
            if valid_algorithms:
                queryset = queryset.filter(algorithm__in=valid_algorithms)

        if coins:
            # Coin filtrini to'g'rilash
            coin_ids = []
            for c in coins:
                try:
                    coin_ids.append(int(c))
                except (ValueError, TypeError):
                    pass
            if coin_ids:
                queryset = queryset.filter(coins__id__in=coin_ids)

        # Price filtrlari
        if price_from:
            try:
                price_from_val = float(price_from)
                if price_from_val >= 0:  # Manfiy qiymatlarni rad etish
                    queryset = queryset.filter(price__gte=price_from_val)
            except (ValueError, TypeError):
                pass

        if price_to:
            try:
                price_to_val = float(price_to)
                if price_to_val > 0:  # Nol va manfiy qiymatlarni rad etish
                    queryset = queryset.filter(price__lte=price_to_val)
            except (ValueError, TypeError):
                pass

        # Stock filtri
        if in_stock and in_stock.lower() in ['true', '1', 'on']:
            queryset = queryset.filter(stock__gt=0)

        # Hashrate filtrlari
        if min_hashrate:
            try:
                min_hashrate_val = float(min_hashrate)
                if min_hashrate_val >= 0:
                    queryset = queryset.filter(hash_rate__gte=min_hashrate_val)
            except (ValueError, TypeError):
                pass

        if max_hashrate:
            try:
                max_hashrate_val = float(max_hashrate)
                if max_hashrate_val > 0:
                    queryset = queryset.filter(hash_rate__lte=max_hashrate_val)
            except (ValueError, TypeError):
                pass

        # Power filtrlari
        if min_power:
            try:
                min_power_val = float(min_power)
                if min_power_val >= 0:
                    queryset = queryset.filter(power_consumption__gte=min_power_val)
            except (ValueError, TypeError):
                pass

        if max_power:
            try:
                max_power_val = float(max_power)
                if max_power_val > 0:
                    queryset = queryset.filter(power_consumption__lte=max_power_val)
            except (ValueError, TypeError):
                pass

        # Sorting
        if sort == "price_asc":
            queryset = queryset.order_by("price", "id")
        elif sort == "price_desc":
            queryset = queryset.order_by("-price", "id")
        elif sort == "new":
            queryset = queryset.order_by("-created_at", "id")
        elif sort == "hashrate_asc":
            queryset = queryset.order_by("hash_rate", "id")
        elif sort == "hashrate_desc":
            queryset = queryset.order_by("-hash_rate", "id")
        else:
            queryset = queryset.order_by("-is_featured", "-created_at", "id")

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # AJAX so'rov uchun JSON response
        if self.request.GET.get('get_filter_data'):
            return self.get_ajax_filter_data()

        # Optimized queryset
        filtered_products = self.get_queryset()

        # Ma'lumotlarni cache qilish
        context['product_count'] = filtered_products.count()

        # Dynamic filtr ma'lumotlari
        context.update(self.get_dynamic_filter_data())

        # Price range
        try:
            price_range = Product.objects.filter(is_active=True).aggregate(
                min_price=Min('price'),
                max_price=Max('price')
            )
            context['min_price'] = max(0, int(price_range['min_price'] or 0))
            context['max_price'] = int(price_range['max_price'] or 10000)
        except (ValueError, TypeError):
            context['min_price'] = 0
            context['max_price'] = 10000

        # Hashrate va Power ranges
        try:
            if filtered_products.exists():
                hashrate_range = filtered_products.aggregate(
                    min_hr=Min('hash_rate'),
                    max_hr=Max('hash_rate')
                )
                power_range = filtered_products.aggregate(
                    min_pw=Min('power_consumption'),
                    max_pw=Max('power_consumption')
                )

                context['min_hashrate'] = max(0, int(hashrate_range['min_hr'] or 0))
                context['max_hashrate'] = int(hashrate_range['max_hr'] or 10000)
                context['min_power'] = max(0, int(power_range['min_pw'] or 0))
                context['max_power'] = int(power_range['max_pw'] or 5000)
            else:
                # Fallback values
                all_products = Product.objects.filter(is_active=True)
                if all_products.exists():
                    ranges = all_products.aggregate(
                        min_hr=Min('hash_rate'),
                        max_hr=Max('hash_rate'),
                        min_pw=Min('power_consumption'),
                        max_pw=Max('power_consumption')
                    )
                    context['min_hashrate'] = max(0, int(ranges['min_hr'] or 0))
                    context['max_hashrate'] = int(ranges['max_hr'] or 10000)
                    context['min_power'] = max(0, int(ranges['min_pw'] or 0))
                    context['max_power'] = int(ranges['max_pw'] or 5000)
                else:
                    # Default values
                    context['min_hashrate'] = 0
                    context['max_hashrate'] = 10000
                    context['min_power'] = 0
                    context['max_power'] = 5000
        except (ValueError, TypeError):
            # Default values on error
            context['min_hashrate'] = 0
            context['max_hashrate'] = 10000
            context['min_power'] = 0
            context['max_power'] = 5000

        # Current slider values
        try:
            context['selected_min_hashrate'] = int(
                self.request.GET.get("min_hashrate", context['min_hashrate'])
            )
            context['selected_max_hashrate'] = int(
                self.request.GET.get("max_hashrate", context['max_hashrate'])
            )
            context['selected_min_power'] = int(
                self.request.GET.get("min_power", context['min_power'])
            )
            context['selected_max_power'] = int(
                self.request.GET.get("max_power", context['max_power'])
            )
        except (ValueError, TypeError):
            context['selected_min_hashrate'] = context['min_hashrate']
            context['selected_max_hashrate'] = context['max_hashrate']
            context['selected_min_power'] = context['min_power']
            context['selected_max_power'] = context['max_power']

        # Saqlangan filtrlar
        context.update({
            "selected_manufacturers": self.request.GET.getlist("manufacturer"),
            "selected_algorithms": self.request.GET.getlist("algorithm"),
            "selected_coins": self.request.GET.getlist("coin"),
            "price_from": self.request.GET.get("price_from", ""),
            "price_to": self.request.GET.get("price_to", ""),
            "in_stock": self.request.GET.get("in_stock", ""),
            "current_sort": self.request.GET.get("sort", ""),
        })

        # Filter statistics
        context['filter_stats'] = self.get_filter_statistics()
        context['partners'] = Manufacturer.objects.filter(is_active=True)[:8]
        if settings.DEBUG:
            context['debug_info'] = {
                'total_products': Product.objects.filter(is_active=True).count(),
                'filtered_count': filtered_products.count(),
                'query_params': dict(self.request.GET.items()),
            }

        return context

    def get_dynamic_filter_data(self):
        """Dynamic filtr ma'lumotlarini olish"""
        filtered_products = self.get_queryset()

        # Joriy tanlangan filtrlarni olish
        selected_manufacturers = self.request.GET.getlist("manufacturer")
        selected_algorithms = self.request.GET.getlist("algorithm")
        selected_coins = self.request.GET.getlist("coin")

        # Manufacturers - faqat filtrlangan productlar asosida
        manufacturers = Manufacturer.objects.filter(
            product__in=filtered_products
        ).distinct().order_by('name').values('id', 'name')

        # Algorithms - faqat filtrlangan productlar asosida
        algorithms = filtered_products.filter(
            algorithm__isnull=False
        ).exclude(algorithm__exact='').values_list('algorithm', flat=True).distinct()

        algorithms_list = sorted([a for a in algorithms if a and a.strip()])

        # Coins - faqat filtrlangan productlar asosida
        coins = Coin.objects.filter(
            products__in=filtered_products
        ).distinct().order_by('name').values('id', 'name')

        return {
            'manufacturers': manufacturers,
            'algorithms': algorithms_list,
            'coins': coins,
        }

    def get_ajax_filter_data(self):
        """AJAX so'rov uchun dynamic filter ma'lumotlari"""
        from django.http import JsonResponse

        # Joriy filtrlangan queryset
        base_queryset = self.get_queryset()

        # Ma'lumotlarni olish
        manufacturers = self.get_manufacturers_data(base_queryset)
        algorithms = self.get_algorithms_data(base_queryset)
        coins = self.get_coins_data(base_queryset)

        return JsonResponse({
            'manufacturers': manufacturers,
            'algorithms': algorithms,
            'coins': coins,
        })

    def get_manufacturers_data(self, queryset):
        """Manufacturer ma'lumotlari"""
        manufacturers = Manufacturer.objects.filter(
            product__in=queryset
        ).distinct().annotate(
            count=Count('product', filter=Q(product__is_active=True))
        ).values('id', 'name', 'count')

        return list(manufacturers)

    def get_algorithms_data(self, queryset):
        """Algorithm ma'lumotlari"""
        # Faqat filtrlangan productlarning algorithmlarini olish
        algorithms = queryset.exclude(
            algorithm__isnull=True
        ).exclude(
            algorithm__exact=''
        ).values('algorithm').annotate(
            count=Count('id')
        ).order_by('algorithm')

        return [{'name': algo['algorithm'], 'count': algo['count']}
                for algo in algorithms if algo['algorithm']]

    def get_coins_data(self, queryset):
        """Coin ma'lumotlari"""
        coins = Coin.objects.filter(
            products__in=queryset
        ).distinct().annotate(
            count=Count('products', filter=Q(products__is_active=True))
        ).values('id', 'name', 'count')

        return list(coins)

    def get_filter_statistics(self):
        """Optimized filter statistics"""
        try:
            base_queryset = Product.objects.filter(is_active=True)

            # Joriy filtrlardan foydalanish
            current_manufacturers = self.request.GET.getlist("manufacturer")
            current_algorithms = self.request.GET.getlist("algorithm")
            current_coins = self.request.GET.getlist("coin")

            # Agar filtrlangan bo'lsa, shu filtrlarga asoslangan statistikani olish
            if current_manufacturers or current_algorithms or current_coins:
                filtered_queryset = self.get_queryset()

                # Manufacturer stats
                manufacturer_stats = {}
                manufacturers = Manufacturer.objects.filter(
                    product__in=filtered_queryset
                ).distinct()

                for man in manufacturers:
                    count = filtered_queryset.filter(manufacturer=man).count()
                    if count > 0:
                        manufacturer_stats[man.id] = count

                # Algorithm stats
                algorithm_stats = {}
                algorithms = filtered_queryset.exclude(
                    algorithm__isnull=True
                ).exclude(
                    algorithm__exact=''
                ).values_list('algorithm', flat=True).distinct()

                for algorithm in algorithms:
                    if algorithm and algorithm.strip():
                        count = filtered_queryset.filter(algorithm=algorithm).count()
                        algorithm_stats[algorithm] = count

                # Coin stats
                coin_stats = {}
                coins = Coin.objects.filter(
                    products__in=filtered_queryset
                ).distinct()

                for coin in coins:
                    count = filtered_queryset.filter(coins=coin).count()
                    if count > 0:
                        coin_stats[coin.id] = count

                return {
                    'manufacturers': manufacturer_stats,
                    'algorithms': algorithm_stats,
                    'coins': coin_stats,
                }

            # Agar filtr bo'lmasa, barcha productlar uchun statistikani olish
            else:
                # Manufacturer stats
                manufacturer_stats = {}
                for m in Manufacturer.objects.all():
                    count = base_queryset.filter(manufacturer=m).count()
                    if count > 0:
                        manufacturer_stats[m.id] = count

                # Algorithm stats
                algorithm_stats = {}
                algorithms = base_queryset.exclude(
                    algorithm__isnull=True
                ).exclude(
                    algorithm__exact=''
                ).values_list('algorithm', flat=True).distinct()

                for algorithm in algorithms:
                    if algorithm and algorithm.strip():
                        count = base_queryset.filter(algorithm=algorithm).count()
                        algorithm_stats[algorithm] = count

                # Coin stats
                coin_stats = {}
                for coin in Coin.objects.all():
                    count = base_queryset.filter(coins=coin).count()
                    if count > 0:
                        coin_stats[coin.id] = count

                return {
                    'manufacturers': manufacturer_stats,
                    'algorithms': algorithm_stats,
                    'coins': coin_stats,
                }

        except Exception as e:
            print(f"Filter statistics error: {e}")
            return {
                'manufacturers': {},
                'algorithms': {},
                'coins': {},
            }

class ProductDetailView(DetailView):
    model = Product
    template_name = "detail.html"
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        discount_info = product.get_discount_info()
        context['discount_info'] = discount_info
        context['delivery'] = DeliveryInfo.objects.first()
        return context

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from asic.models import Product
from .cart import Cart  # Cart klassini import qiling

# CART
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    cart.add(product=product, quantity=quantity, update_quantity=False)
    return redirect(request.META.get('HTTP_REFERER', '/'))

def add_cart_buy(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.add(product)

    return redirect('asic:checkout')

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    return redirect('asic:cart_detail')

def update_cart_quantity(request, product_id):
    """Cart'dagi mahsulot miqdorini yangilash"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)

        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity <= 0:
                # Agar quantity 0 yoki manfiy bo'lsa, mahsulotni o'chirish
                cart.remove(product)
            else:
                # Quantity'ni yangilash
                cart.add(product=product, quantity=quantity, update_quantity=True)
        except (ValueError, TypeError):
            pass  # Noto'g'ri qiymat bo'lsa, hech narsa qilmaslik

    return redirect('asic:cart_detail')

def cart_detail(request):
    cart = Cart(request)

    # Yaroqsiz itemlarni tozalash
    cart.clean_invalid_items()

    # Savatchadagi barcha mahsulotlarni olish
    try:
        cart_items = list(cart)
    except Exception as e:
        print(f"Cart iteration error: {e}")
        cart_items = []

    # Filtrlangan cart items - faqat valid mahsulotlar
    valid_cart_items = []

    for item in cart_items:
        if ('product' in item and
            hasattr(item['product'], 'id') and
            item['product'].id is not None and
            str(item['product'].id).strip() != ''):

            try:
                item['remove_url'] = reverse('asic:remove_from_cart', args=[item['product'].id])
                valid_cart_items.append(item)
            except Exception as e:
                print(f"URL reverse error for product {item.get('product', 'Unknown')}: {e}")
                continue
        else:
            print(f"Invalid item found: {item}")

    context = {
        'cart': valid_cart_items,
        'cart_total': cart.get_total_price(),
        'cart_count': len(cart),
    }
    return render(request, 'cart/cart.html', context)

@login_required
@transaction.atomic
def checkout(request):
    cart = Cart(request)

    if not cart:
        messages.error(request, "Корзина пуста.")
        return redirect('asic:cart_detail')

    # Stock validation - check if all cart items have sufficient stock
    stock_errors = []
    for item in cart:
        product = item['product']
        quantity = item['quantity']
        # Refresh product from database to get latest stock
        product.refresh_from_db()

        if product.stock < quantity:
            stock_errors.append({
                'product': product,
                'requested': quantity,
                'available': product.stock
            })

    # If there are stock errors, redirect back to cart with error messages
    if stock_errors:
        for error in stock_errors:
            if error['available'] == 0:
                messages.error(
                    request,
                    f"Товар '{error['product'].name}' закончился на складе."
                )
            else:
                messages.error(
                    request,
                    f"Товар '{error['product'].name}': запрошено {error['requested']} шт., "
                    f"доступно только {error['available']} шт."
                )
        return redirect('asic:cart_detail')

    # Faqat aktiv delivery sozlamalarini olish
    try:
        delivery_settings = DeliverySettings.objects.get(is_active=True)
    except DeliverySettings.DoesNotExist:
        messages.error(request, "Настройки доставки не найдены.")
        return redirect('asic:cart_detail')
    except DeliverySettings.MultipleObjectsReturned:
        delivery_settings = DeliverySettings.objects.filter(is_active=True).first()
        messages.warning(request, "Найдено несколько активных настроек доставки. Используется первая.")

    def calculate_delivery_cost(cart, delivery_type, delivery_settings):
        """Yetkazib berish narxini hisoblash (har bir mahsulot uchun)"""
        total_delivery = Decimal('0')
        if delivery_type == 'air':
            delivery_rate = delivery_settings.air_delivery_rate
        elif delivery_type == 'sea':
            delivery_rate = delivery_settings.sea_delivery_rate
        elif delivery_type == 'auto':
            delivery_rate = delivery_settings.auto_delivery_rate
        else:
            delivery_rate = delivery_settings.air_delivery_rate

        for item in cart:
            quantity = Decimal(str(item['quantity']))
            total_delivery += delivery_rate * quantity

        return total_delivery

    def calculate_document_cost(cart_total, document_type, delivery_settings):
        """Hujjat narxini hisoblash (umumiy summadan foiz)"""
        if document_type == 'gtd_rb':
            percentage = delivery_settings.gtd_rb_cost
        else:  # dt_rf
            percentage = delivery_settings.dt_rf_cost

        return cart_total * (percentage / Decimal('100'))

    if request.method == 'POST':
        # Before processing POST request, validate stock again
        stock_errors = []
        for item in cart:
            product = item['product']
            quantity = item['quantity']

            # Refresh product from database to get latest stock info
            product.refresh_from_db()

            if product.stock < quantity:
                stock_errors.append({
                    'product': product,
                    'requested': quantity,
                    'available': product.stock
                })

        # If stock validation fails during POST, redirect with errors
        if stock_errors:
            for error in stock_errors:
                if error['available'] == 0:
                    messages.error(
                        request,
                        f"Товар '{error['product'].name}' закончился на складе."
                    )
                else:
                    messages.error(
                        request,
                        f"Товар '{error['product'].name}': запрошено {error['requested']} шт., "
                        f"доступно только {error['available']} шт."
                    )
            return redirect('asic:cart_detail')

        # User information
        username = request.POST.get('username')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        discount_percentage = request.POST.get('discount_percentage')
        # Address information
        country = request.POST.get('country')
        address_region = request.POST.get('address_region')
        address_city = request.POST.get('address_city')
        address_street = request.POST.get('address_street')
        house = request.POST.get('house')
        block = request.POST.get('block', '')
        apartment = request.POST.get('apartment', '')
        address_postal_code = request.POST.get('address_postal_code')

        # Order details
        notes = request.POST.get('notes', '')
        delivery_type = request.POST.get('delivery_type', 'air')
        document_type = request.POST.get('document_type', 'gtd_rb')

        # Calculated prices from form
        delivery_fee_from_form = request.POST.get('delivery_fee')
        document_fee_from_form = request.POST.get('document_fee')
        grand_total_from_form = request.POST.get('grand_total')

        # Validatsiya
        valid_delivery_types = dict(Order.DELIVERY_TYPES).keys()
        valid_document_types = dict(Order.DOCUMENT_TYPES).keys()
        if delivery_type not in valid_delivery_types:
            delivery_type = 'air'
        if document_type not in valid_document_types:
            document_type = 'gtd_rb'

        # Full name yasash
        full_name_parts = []
        if last_name:
            full_name_parts.append(last_name)
        if first_name:
            full_name_parts.append(first_name)
        if middle_name:
            full_name_parts.append(middle_name)
        full_name = ' '.join(full_name_parts) if full_name_parts else username

        shipping_address = f"""
        ФИО: {full_name}
        Тел: {phone}
        Адрес: {country}, {address_region}, {address_city}, {address_street} {house}
        {f"Корпус: {block}" if block else ""}
        {f"Квартира: {apartment}" if apartment else ""}
        {f"Почтовый индекс: {address_postal_code}" if address_postal_code else ""}
        """.strip()

        # 1. Cart subtotal va individual discounts hisoblash
        cart_subtotal = Decimal('0')
        cart_items_data = []

        for item in cart:
            product = item['product']
            quantity = Decimal(str(item['quantity']))
            # Cart obyektida allaqachon discount qo'llanilgan narx bor
            final_price = Decimal(str(item['price']))

            # Mahsulot total (allaqachon discount bilan)
            item_total = final_price * quantity
            cart_subtotal += item_total

            # Original price olish uchun discount ma'lumotlarini olish
            original_discount_info = calculate_product_discount(product, product.price, Decimal('0'))
            original_price = Decimal(str(product.price))
            product_discount = (original_price - final_price) * quantity

            # Prepare cart item data for payment
            cart_items_data.append({
                'product_id': product.id,
                'quantity': float(quantity),
                'original_price': float(original_price),
                'discounted_price': float(final_price),
                'product_discount': float(product_discount),
                'item_total': float(item_total),
                'applied_discounts': original_discount_info['applied_discounts']
            })

        # 2. Additional discount (is_additional=True) ni faqat cart_subtotal ga qo'llash
        # Including first order discount
        cart_discount_info = calculate_cart_total_discount(cart_subtotal, request.user)
        discounted_cart_total = cart_discount_info['final_cart_total']
        cart_discount = cart_discount_info['cart_discount']

        # 3. Delivery va document costlarni hisoblash
        # Agar formdan kelgan narxlar bo'lsa, ularni ishlatish
        if delivery_fee_from_form and document_fee_from_form and grand_total_from_form:
            try:
                delivery_cost = Decimal(delivery_fee_from_form)
                document_cost = Decimal(document_fee_from_form)
                final_checkout_total = Decimal(grand_total_from_form)

                print(f"Using form values: delivery={delivery_cost}, document={document_cost}, total={final_checkout_total}")
            except (ValueError, TypeError) as e:
                print(f"Error parsing form values: {e}. Using calculated values.")
                # Xatolik bo'lsa, oddiy hisob-kitobni ishlatish
                delivery_cost = calculate_delivery_cost(cart, delivery_type, delivery_settings)
                document_cost = calculate_document_cost(cart_subtotal, document_type, delivery_settings)
                final_checkout_total = discounted_cart_total + delivery_cost + document_cost
        else:
            # Eskicha hisob-kitob
            delivery_cost = calculate_delivery_cost(cart, delivery_type, delivery_settings)
            document_cost = calculate_document_cost(cart_subtotal, document_type, delivery_settings)
            final_checkout_total = discounted_cart_total + delivery_cost + document_cost

        # Calculate product discount total
        product_discount_total = Decimal('0')
        for item_data in cart_items_data:
            product_discount_total += Decimal(str(item_data['product_discount']))

        # Generate unique billing ID
        billing_id = str(uuid.uuid4())

        # Har bir mahsulot uchun delivery cost hisoblash
        if delivery_type == 'air':
            delivery_rate = delivery_settings.air_delivery_rate
        elif delivery_type == 'sea':
            delivery_rate = delivery_settings.sea_delivery_rate
        elif delivery_type == 'auto':
            delivery_rate = delivery_settings.auto_delivery_rate
        else:
            delivery_rate = delivery_settings.air_delivery_rate

        # Add delivery cost to each cart item
        for item_data in cart_items_data:
            quantity = Decimal(str(item_data['quantity']))
            item_delivery_cost = delivery_rate * quantity
            item_data['delivery_cost_per_unit'] = float(delivery_rate)
            item_data['total_delivery_cost'] = float(item_delivery_cost)

        # Serializable applied cart discounts
        serializable_cart_discounts = []
        for discount_info in cart_discount_info['applied_cart_discounts']:
            discount_data = {
                'discount_type': discount_info['discount_type'],
                'discount_name': discount_info['discount_name'],
                'discount_amount': float(discount_info['discount_amount']),
                'discount_percent': float(discount_info['discount_percent']),
                'is_first_order': discount_info.get('is_first_order', False)
            }

            if discount_info.get('discount'):
                # Regular discount
                discount = discount_info['discount']
                discount_data.update({
                    'discount_id': discount.id,
                    'discount_value': float(discount.value)
                })
            else:
                # First order discount (virtual)
                discount_data.update({
                    'discount_id': None,
                    'discount_value': None,
                    'discount_description': discount_info.get('discount_description', ''),
                    'rate': discount_info.get('rate', 0)
                })

            serializable_cart_discounts.append(discount_data)

        # Debug ma'lumotlari
        print(f"DEBUG - Checkout Calculation:")
        print(f"Cart subtotal: {cart_subtotal}")
        print(f"Discounted cart total: {discounted_cart_total}")
        print(f"Delivery cost: {delivery_cost} (type: {delivery_type}, rate: {delivery_rate})")
        print(f"Document cost: {document_cost} (type: {document_type})")
        print(f"Final total: {final_checkout_total}")
        print(f"Using form values: {bool(delivery_fee_from_form and document_fee_from_form and grand_total_from_form)}")
        print(f"test dicount_percentage {discount_percentage}")
        if discount_percentage:
            discount_percentage = discount_percentage.replace(',', '.')
            try:
                discount_percentage = Decimal(discount_percentage)
            except InvalidOperation:
                discount_percentage = Decimal('0')
        else:
            discount_percentage = Decimal('0')
        # Save payment before redirect
        payment = Payment.objects.create(
            client=request.user,
            billing_id=billing_id,
            email=email,
            currency="USD",
            amount=final_checkout_total,
            status='в обработке',
            temp_data={
                # User info
                'full_name': full_name,
                'phone': phone,
                'email': email,

                # Address info
                'country': country,
                'region': address_region,
                'city': address_city,
                'street': address_street,
                'house': house,
                'block': block,
                'apartment': apartment,
                'postal_code': address_postal_code,
                'shipping_address': shipping_address,
                'notes': notes,

                # Order details
                'delivery_type': delivery_type,
                'document_type': document_type,

                # Financial data
                'cart_subtotal': float(cart_subtotal),
                'discounted_cart_total': float(discounted_cart_total),
                'product_discount_total': float(product_discount_total),
                'cart_discount': float(cart_discount),
                'delivery_cost': float(delivery_cost),
                'document_cost': float(document_cost),
                'document_percentage': float(delivery_settings.gtd_rb_cost if document_type == 'gtd_rb' else delivery_settings.dt_rf_cost),
                'total': float(final_checkout_total),
                'discount_percentage' : float(discount_percentage) if discount_percentage else 4.0,
                'final_checkout_total': float(final_checkout_total),

                # Cart items
                'cart_items': cart_items_data,
                'applied_cart_discounts': serializable_cart_discounts,

                # Technical data
                'delivery_rate_used': float(delivery_rate),
                'calculated_from_form': bool(delivery_fee_from_form and document_fee_from_form and grand_total_from_form)
            }
        )


        # CryptoCloud API so'rovi
        payload = {
            "shop_id": settings.CRYPTOCLOUD_SHOP_ID,
            "amount": float(final_checkout_total),
            "currency": "USD",
            "order_id": billing_id,
            "email": email,
            "success_url": request.build_absolute_uri(reverse('payments:payment_success')),
            "fail_url": request.build_absolute_uri(reverse('payments:payment_fail')),
            "callback_url": request.build_absolute_uri(reverse('callback')),
        }
        headers = {
            "Authorization": f"Token {settings.CRYPTOCLOUD_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                "https://api.cryptocloud.plus/v2/invoice/create",
                json=payload,
                headers=headers,
                timeout=15
            )
            result = response.json()

            if result.get("status") == "success" and result.get("result") and result["result"].get("link"):
                return redirect(result["result"]["link"])
            else:
                messages.error(request, "Ошибка при создании платёжной ссылки.")
                print("Payment API Error:", result)

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Ошибка соединения с сервером: {e}")
            print("RequestException during payment init:", e)
        except ValueError as e:
            messages.error(request, f"Ошибка обработки ответа сервера: {e}")
            print("JSON decode error:", e)

        return redirect("asic:checkout")

    # GET request - template uchun ma'lumotlarni hisoblash
    # Validate stock for GET request as well
    stock_errors = []
    for item in cart:
        product = item['product']
        quantity = item['quantity']
        if product.stock < quantity:
            stock_errors.append({
                'product': product,
                'requested': quantity,
                'available': product.stock
            })

    # If there are stock errors in GET request, show warnings and redirect to cart
    if stock_errors:
        for error in stock_errors:
            if error['available'] == 0:
                messages.warning(
                    request,
                    f"Товар '{error['product'].name}' закончился на складе. "
                    f"Пожалуйста, удалите его из корзины."
                )
            else:
                messages.warning(
                    request,
                    f"Товар '{error['product'].name}': в корзине {error['requested']} шт., "
                    f"доступно только {error['available']} шт. Пожалуйста, измените количество."
                )
        return redirect('asic:cart_detail')

    cart_subtotal = Decimal('0')
    cart_items_with_discounts = []

    # Cart obyektidan to'g'ridan-to'g'ri foydalanish
    for item in cart:
        product = item['product']
        quantity = Decimal(str(item['quantity']))
        # Cart obyektida allaqachon discount qo'llanilgan narx bor
        final_price = Decimal(str(item['price']))

        # Calculate item total with already applied discount
        item_total = final_price * quantity
        cart_subtotal += item_total

        # Original price va discount ma'lumotlarini olish
        original_discount_info = calculate_product_discount(product, product.price, Decimal('0'))
        original_price = Decimal(str(product.price))
        product_discount = (original_price - final_price) * quantity

        # Prepare cart item data for template
        item_data = item.copy()
        item_data['original_price'] = original_price
        item_data['discounted_price'] = final_price
        item_data['product_discount'] = product_discount
        item_data['item_total'] = item_total
        item_data['applied_discounts'] = original_discount_info['applied_discounts']
        item_data['delivery_cost_per_unit'] = delivery_settings.air_delivery_rate
        item_data['total_delivery_cost'] = delivery_settings.air_delivery_rate * quantity

        cart_items_with_discounts.append(item_data)

    # Calculate product discount total for template
    product_discount_total = Decimal('0')
    for item_data in cart_items_with_discounts:
        product_discount_total += item_data['product_discount']

    # Additional discount (is_additional=True) ni faqat cart_subtotal ga qo'llash
    # Including first order discount
    cart_discount_info = calculate_cart_total_discount(cart_subtotal, request.user)
    discounted_cart_total = cart_discount_info['final_cart_total']
    cart_discount = cart_discount_info['cart_discount']

    # Total discount percent hisoblash
    total_discount_percent = Decimal('0')
    for discount_info in cart_discount_info['applied_cart_discounts']:
        total_discount_percent += Decimal(str(discount_info.get('discount_percent', 0)))

    # Delivery va document costs
    default_delivery_cost = calculate_delivery_cost(cart, 'air', delivery_settings)
    default_document_cost = calculate_document_cost(cart_subtotal, 'gtd_rb', delivery_settings)

    # Final total = discounted cart + delivery + document
    final_checkout_total = discounted_cart_total + default_delivery_cost + default_document_cost

    context = {
        'cart': cart_items_with_discounts,
        'cart_subtotal': cart_subtotal,
        'discounted_cart_total': discounted_cart_total,
        'product_discount_total': product_discount_total,
        'cart_discount': cart_discount,
        'final_checkout_total': final_checkout_total,
        'total_discount_percent': total_discount_percent,
        'applied_cart_discounts': cart_discount_info['applied_cart_discounts'],
        'default_delivery_cost': default_delivery_cost,
        'default_document_cost': default_document_cost,
        'default_document_percentage': delivery_settings.gtd_rb_cost,
        'delivery_types': [
            ('air', delivery_settings.air_delivery_name),
            ('sea', delivery_settings.sea_delivery_name),
            ('auto', delivery_settings.auto_delivery_name)
        ],
        'document_types': [
            ('gtd_rb', delivery_settings.gtd_rb_name),
            ('dt_rf', delivery_settings.dt_rf_name)
        ],
        'delivery_settings': delivery_settings,
        'page_titles': {'checkout': 'Оформление заказа'},
    }

    return render(request, 'checkout.html', context)


from datetime import datetime

def generate_order_number():
    # Masalan: ORD-202507221845-XXXX
    return f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"




@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()

        profile.phone = request.POST.get('phone', profile.phone)
        profile.first_name = request.POST.get('first_name', profile.first_name)
        profile.last_name = request.POST.get('last_name', profile.last_name)
        profile.father_name = request.POST.get('middle_name', profile.father_name)

        profile.country = request.POST.get('country', profile.country)
        profile.home = request.POST.get('home', profile.home)
        profile.address_street = request.POST.get('address_street', profile.address_street)
        profile.address_city = request.POST.get('address_city', profile.address_city)
        profile.address_region = request.POST.get('address_region', profile.address_region)
        profile.address_postal_code = request.POST.get('address_postal_code', profile.address_postal_code)

        profile.save()

        return redirect('asic:profile')

    orders = Order.objects.filter(user=user).order_by('-created_at')

    return render(request, 'profile.html', {
        'user': user,
        'orders': orders,
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order-detail.html', {'order': order})

class AboutPage(ListView):
    template_name = 'about.html'
    model  = Office
    context_object_name = 'offices'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['settings'] = About_page.objects.all().first()
        return context

def static_page_view(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    return render(request, 'static_page.html', {'page': page})


def paymentview(request):
    context = {}
    context['settings'] = PayCheck.objects.all().first()
    return render(request, 'payment-check.html',context)

def privacy(request):
    context = {}
    context['settings'] = Privacy.objects.all().first()

    return render(request,'privacy.html',context)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'new':
        order.status = 'cancelled'
        order.save()
        messages.success(request, "Заказ успешно отменён.")
    else:
        messages.error(request, "Отменить заказ нельзя.")

    return redirect(reverse('asic:order_detail', args=[order_id]))

from .models import DeliveryInfo

def product_detail(request, pk):
    delivery = DeliveryInfo.objects.first()
    return render(request, "product_detail.html", {"delivery": delivery})


@login_required
def order_list(request):
    """User'ning barcha orderlarini ko'rsatish"""
    # Faqat current user'ning orderlari
    orders = Order.objects.filter(user=request.user).select_related(
        'user'
    ).prefetch_related(
        'items__product',
        'items__product__manufacturer'
    ).order_by('-created_at')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        orders = orders.filter(status=status_filter)

    # Pagination
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get status choices for filter
    status_choices = Order.STATUS_CHOICES

    # Calculate statistics
    total_orders = orders.count()
    total_spent = sum([order.total for order in orders])
    completed_orders = orders.filter(status='completed').count()
    pending_orders = orders.filter(status__in=['new', 'processing']).count()

    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
        'status_choices': status_choices,
        'current_status': status_filter or 'all',
        'total_orders': total_orders,
        'total_spent': total_spent,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
    }

    return render(request, 'order_list.html', context)
