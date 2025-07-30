import uuid
from django.db import transaction
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView,DetailView,ListView
from .models import Product,Manufacturer,Order,OrderItem,DeliverySettings,BannerImage,Profile,Office
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


class HomeView(ListView):
    template_name = "index.html"
    model = Product
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        active_banner = BannerImage.objects.filter(is_active=True).first()
        context['products'] = Product.objects.all()[:3]
        
        context['active_banner'] = active_banner
        return context
    
class CatalogView(ListView):
    template_name = "catalog.html"
    model = Product
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        manufacturers = self.request.GET.getlist("manufacturer")
        algorithms = self.request.GET.getlist("algorithm")
        price_from = self.request.GET.get("price_from")
        price_to = self.request.GET.get("price_to")
        in_stock = self.request.GET.get("in_stock")
        sort = self.request.GET.get("sort")
        
        if manufacturers:
            queryset = queryset.filter(manufacturer__id__in=manufacturers)

        if algorithms:
            queryset = queryset.filter(algorithm__in=algorithms)

        if price_from:
            queryset = queryset.filter(price__gte=price_from)
        if price_to:
            queryset = queryset.filter(price__lte=price_to)

        if in_stock:
            queryset = queryset.filter(stock__gt=0)
        if sort == "price_asc":
            queryset = queryset.order_by("price")
        elif sort == "price_desc":
            queryset = queryset.order_by("-price")
        elif sort == "new":
            queryset = queryset.order_by("-created_at") 
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_products = self.get_queryset()
        context['product_count'] = filtered_products.count() 
        context['manufacturers'] = Manufacturer.objects.all()
        context['algorithms'] = Product.objects.values_list('algorithm', flat=True).distinct()

        context["selected_manufacturers"] = self.request.GET.getlist("manufacturer")
        context["selected_algorithms"] = self.request.GET.getlist("algorithm")
        context["price_from"] = self.request.GET.get("price_from", "")
        context["price_to"] = self.request.GET.get("price_to", "")
        context["in_stock"] = self.request.GET.get("in_stock", "")

        return context

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
            "success_url": "https://76628715a526.ngrok-free.app/payments/success",
            "fail_url": "https://76628715a526.ngrok-free.app/payments/failed",
            "callback_url": "https://76628715a526.ngrok-free.app/payments/callback",
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

    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        user.email = email
        user.save()

        profile, created = Profile.objects.get_or_create(user=user)
        profile.phone = phone
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