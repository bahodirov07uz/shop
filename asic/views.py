
import uuid
from django.db import transaction
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView,DetailView,ListView
from .models import Product,Manufacturer,Order,OrderItem,DeliverySettings,BannerImage,Profile,Office,StaticPage
from django.core.paginator import Paginator
from .cart import Cart
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_POST
from payments.models import Payment
import requests
from django.db.models import Max,Min,Count

class HomeView(ListView):
    template_name = "index.html"
    model = Product
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        active_banner = BannerImage.objects.filter(is_active=True).first()
        context['products'] = Product.objects.all()[:3]
        
        context['active_banner'] = active_banner
        return context
    
from django.views.generic import ListView
from django.db.models import Q
from .models import Product, Manufacturer, Coin

from django.db.models import Min, Max, Q, Count
from django.views.generic import ListView
from .models import Product, Manufacturer, Coin

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
            queryset = queryset.order_by("price", "id")  # id qo'shildi consistency uchun
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
        
        # Optimized queryset
        filtered_products = self.get_queryset()
        
        # Ma'lumotlarni cache qilish
        context['product_count'] = filtered_products.count()

        # Manufacturers - prefetch bilan optimizatsiya
        context['manufacturers'] = Manufacturer.objects.filter(
            product__is_active=True
        ).distinct().order_by('name').values('id', 'name')

        # Algorithms - bo'sh qiymatlarni filtrlash
        algorithms = Product.objects.filter(
            is_active=True,
            algorithm__isnull=False
        ).exclude(algorithm__exact='').values_list('algorithm', flat=True).distinct()
        
        context['algorithms'] = sorted([a for a in algorithms if a and a.strip()])

        # Coins - optimized
        context['coins'] = Coin.objects.filter(
            products__is_active=True
        ).distinct().order_by('name').values('id', 'name')

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

        # Hashrate va Power ranges - null qiymatlarni handle qilish
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
        
        # Debug ma'lumotlari (development uchun)
        if settings.DEBUG:
            context['debug_info'] = {
                'total_products': Product.objects.filter(is_active=True).count(),
                'filtered_count': filtered_products.count(),
                'query_params': dict(self.request.GET.items()),
            }

        return context

    def get_filter_statistics(self):
        """Optimized filter statistics"""
        try:
            base_queryset = Product.objects.filter(is_active=True)
            
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
            # Log error and return empty stats
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
        return context

# CART
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
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

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})



@login_required
@transaction.atomic
def checkout(request):
    cart = Cart(request)

    if not cart:
        messages.error(request, "Корзина пуста.")
        return redirect('asic:cart_detail')

    delivery_settings = DeliverySettings.objects.filter(is_active=True).first()
    if not delivery_settings:
        messages.error(request, "Настройки доставки не найдены.")
        return redirect('asic:cart_detail')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        country = request.POST.get('country')
        region = request.POST.get('region')
        city = request.POST.get('city')
        street = request.POST.get('street')
        house = request.POST.get('house')
        block = request.POST.get('block', '')
        apartment = request.POST.get('apartment', '')
        notes = request.POST.get('notes', '')
        delivery_type = request.POST.get('delivery_type', 'air')
        document_type = request.POST.get('document_type', 'gtd_rb')

        valid_delivery_types = dict(Order.DELIVERY_TYPES).keys()
        valid_document_types = dict(Order.DOCUMENT_TYPES).keys()
        if delivery_type not in valid_delivery_types:
            delivery_type = 'air'
        if document_type not in valid_document_types:
            document_type = 'gtd_rb'

        shipping_address = f"""
        ФИО: {full_name}
        Тел: {phone}
        Адрес: {country}, {region}, {city}, {street} {house}
        {f"Корпус: {block}" if block else ""}
        {f"Квартира: {apartment}" if apartment else ""}
        """.strip()

        subtotal = Decimal(str(cart.get_total_price()))
        delivery_cost = delivery_settings.air_delivery_rate if delivery_type == 'air' else delivery_settings.sea_delivery_rate
        document_cost = delivery_settings.gtd_rb_cost if document_type == 'gtd_rb' else delivery_settings.dt_rf_cost
        total = subtotal + delivery_cost + document_cost

        # Generate unique billing ID
        billing_id = str(uuid.uuid4())

        # Save payment before redirect
        payment = Payment.objects.create(
            client=request.user,
            billing_id=billing_id,
            email=email,
            currency="USD",
            amount=total,
            status='pending',
            temp_data={
                'full_name': full_name,
                'phone': phone,
                'email': email,
                'country': country,
                'region': region,
                'city': city,
                'street': street,
                'house': house,
                'block': block,
                'apartment': apartment,
                'notes': notes,
                'delivery_type': delivery_type,
                'document_type': document_type,
                'shipping_address': shipping_address,
                'subtotal': float(subtotal),
                'delivery_cost': float(delivery_cost),
                'document_cost': float(document_cost),
                'total': float(total),
                'cart_items': [
                    {
                        'product_id': item['product'].id,
                        'quantity': item['quantity'],
                        'price': float(item['price']),
                    } for item in cart
                ]
            }
        )

        # CryptoCloud API so‘rovi
        payload = {
            "shop_id": settings.CRYPTOCLOUD_SHOP_ID,
            "amount": float(total),
            "currency": "USD",
            "order_id": billing_id,
            "email": email,
            "success_url": "https://china-asic.com/payments/success",
            "fail_url": "https://china-asic.com/payments/failed",
            "callback_url": "https://china-asic.com/payments/callback",
        }

        headers = {
            "Authorization": f"Token {settings.CRYPTOCLOUD_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post("https://api.cryptocloud.plus/v2/invoice/create", json=payload, headers=headers, timeout=15)
            result = response.json()
            print("Payment init result:", result)

            if result.get("status") == "success" and result.get("result") and result["result"].get("link"):
                return redirect(result["result"]["link"])
            else:
                messages.error(request, "Ошибка при создании платёжной ссылки.")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Ошибка соединения с сервером: {e}")
            print("RequestException during payment init:", e)
        except ValueError as e:
            messages.error(request, f"Ошибка обработки ответа сервера: {e}")
            print("JSON decode error:", e)

        return redirect("asic:checkout")

    context = {
        'cart': cart,
        'cart_total': cart.get_total_price(),
        'delivery_types': [
            ('air', f"Авиадоставка - {delivery_settings.air_delivery_rate} $"),
            ('sea', f"Морская доставка - {delivery_settings.sea_delivery_rate} $")
        ],
        'document_types': [
            ('gtd_rb', f"ГТД РБ - {delivery_settings.gtd_rb_cost} $"),
            ('dt_rf', f"ДТ РФ - {delivery_settings.dt_rf_cost} $")
        ],
        'delivery_settings': delivery_settings,
    }
    return render(request, 'checkout.html', context)

from datetime import datetime

def generate_order_number():
    # Masalan: ORD-202507221845-XXXX
    return f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

@login_required
def profile_view(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'orders': orders,
    }
    return render(request, 'profile.html', context)


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.save()

        # Profile ma'lumotlari
        profile.phone = request.POST.get('phone', profile.phone)
        profile.first_name = request.POST.get('first_name', profile.first_name)
        profile.last_name = request.POST.get('last_name', profile.last_name)
        profile.father_name = request.POST.get('middle_name', profile.father_name)
        profile.save()

        profile, created = Profile.objects.get_or_create(user=user)
        profile.save()

        return redirect('asic:profile')  # Sahifani yangilash uchun

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
    
    
def static_page_view(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    return render(request, 'static_page.html', {'page': page})


def paymentview(request):
    return render(request, 'payment-check.html')

def privacy(request):
    return render(request,'privacy.html')