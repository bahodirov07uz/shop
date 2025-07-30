from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Payment
from .utils import verify_signature
from asic.models import Order, OrderItem
from asic.models import Product
from asic.views import generate_order_number  # agar bunday funksiya bo‘lsa
from django.shortcuts import render
import json

@csrf_exempt
def payment_callback(request):
    if request.method != 'POST':
        return HttpResponse("Only POST allowed", status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON", status=400)

    if not verify_signature(data):
        return HttpResponse("Invalid signature", status=403)

    billing_id = data.get("order_id")
    status = data.get("status")

    try:
        payment = Payment.objects.get(billing_id=billing_id)
    except Payment.DoesNotExist:
        return HttpResponse("Payment not found", status=404)

    if status == "paid" and payment.status != 'success':
        payment.status = 'success'
        payment.payment_id = data.get("uuid")
        payment.save()

        order_data = payment.temp_data
        if order_data:
            order = Order.objects.create(
                user=payment.client,
                order_number=billing_id,
                delivery_type=order_data['delivery_type'],
                delivery_cost=order_data['delivery_cost'],
                document_type=order_data['document_type'],
                document_cost=order_data['document_cost'],
                subtotal=order_data['subtotal'],
                total=order_data['total'],
                shipping_address=order_data['shipping_address'],
                billing_address=order_data['shipping_address'],
                notes=order_data['notes'],
                payment_status='paid'
            )

            for item in order_data['cart_items']:
                OrderItem.objects.create(
                    order=order,
                    product=Product.objects.get(id=item['product_id']),
                    quantity=item['quantity'],
                    price=item['price']
                )

    return HttpResponse("OK")

def payment_success(request):
    return render(request, 'payments/success.html')

def payment_failed(request):
    return render(request, 'payments/failed.html')