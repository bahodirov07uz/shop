# payments/views.py

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import transaction
from .models import Payment
from asic.models import Order, OrderItem, Product
from asic.cart import Cart
from decimal import Decimal
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def payment_callback(request):
    logger.info("📩 Получен callback")

    if request.method != "POST":
        return HttpResponse("Только POST разрешен", status=405)

    # 🔹 Получение данных
    data = None
    try:
        if request.body:
            raw_body = request.body.decode("utf-8")
            logger.info(f"📦 Raw callback body: {raw_body}")
            
            try:
                data = json.loads(raw_body)
                logger.info(f"📦 JSON callback data: {data}")
            except json.JSONDecodeError:
                data = request.POST.dict()
                logger.info(f"📦 FORM callback data: {data}")
    except Exception as e:
        logger.exception(f"❌ Ошибка парсинга callback: {str(e)}")
        return HttpResponse("Неверный запрос", status=400)

    if not data:
        logger.error("❌ Нет данных в callback")
        return HttpResponse("Пустое тело запроса", status=400)

    # 🔹 Получение Billing ID
    billing_id = data.get("billing_id") or data.get("order_id")
    if not billing_id:
        logger.error("❌ Нет order_id")
        return HttpResponse("order_id обязателен", status=400)

    logger.info(f"✅ Проверка подписи пропущена для тестирования")

    # 🔹 Находим платеж
    try:
        payment = Payment.objects.get(billing_id=billing_id)
        logger.info(f"✅ Платеж найден: id={payment.id}, статус={payment.status}")
    except Payment.DoesNotExist:
        logger.error(f"❌ Платеж не найден: {billing_id}")
        return HttpResponse("Платеж не найден", status=404)

    # 🔹 Определяем статус
    status = (data.get("status") or "").lower()
    logger.info(f"📌 Статус callback: {status}")

    success_statuses = {"paid", "success", "confirmed", "успешно", "оплачен", "подтверждено"}
    failed_statuses = {"failed", "cancelled", "rejected", "ошибка", "отменено", "отклонено"}

    # 🔹 Защита от дублирующих callback'ов
    if payment.status == "успешно" and status in success_statuses:
        logger.info("ℹ️ Дублирующий успешный callback — игнорируем")
        return HttpResponse("OK")

    if status in success_statuses:
        try:
            with transaction.atomic():
                payment.status = "успешно"
                if data.get("uuid"):
                    payment.invoice_uuid = data.get("uuid")
                payment.save()
                logger.info(f"✅ Статус платежа обновлен на 'успешно'")

                # Проверяем существование заказа
                if Order.objects.filter(payment_id=payment.billing_id).exists():
                    logger.info(f"ℹ️ Заказ уже существует для платежа {payment.id}")
                else:
                    order_data = payment.temp_data or {}
                    logger.info(f"📦 Данные заказа из temp_data: {order_data}")
                    
                    if not order_data:
                        logger.error(f"❌ Нет temp_data для платежа {payment.id}")
                        raise ValueError("Нет temp_data для платежа")

                    # Создаем заказ
                    order_number = f"ORD{payment.id:06d}"
                    
                    order = Order.objects.create(
                        user=payment.client,
                        order_number=order_number,
                        delivery_type=order_data.get("delivery_type", "air"),
                        delivery_cost=Decimal(str(order_data.get("delivery_cost", 0))),
                        document_type=order_data.get("document_type", "gtd_rb"),
                        document_cost=Decimal(str(order_data.get("document_cost", 0))),
                        subtotal=Decimal(str(order_data.get("cart_subtotal", 0))),
                        discount_amount=Decimal(str(order_data.get("cart_discount", 0) or 0)),
                        discount_percent=Decimal(str(order_data.get("discount_percentage", 0) or 0)),
                        total=Decimal(str(order_data.get("total", 0))),
                        shipping_address=order_data.get("shipping_address", ""),
                        notes=order_data.get("notes", ""),
                        payment_status="оплачен",
                        payment_id=payment.billing_id
                    )
                    logger.info(f"✅ Заказ создан: {order.id}")

                    # Создаем OrderItems
                    cart_items = order_data.get("cart_items", [])
                    logger.info(f"🛒 Создание {len(cart_items)} позиций заказа")
                    
                    for item in cart_items:
                        product_id = item.get("product_id")
                        qty = int(item.get("quantity", 0))
                        
                        try:
                            product = Product.objects.select_for_update().get(id=product_id)
                            logger.info(f"✅ Товар найден: {product.id}, остаток: {product.stock}")
                            
                            if product.stock >= qty:
                                OrderItem.objects.create(
                                    order=order,
                                    product=product,
                                    quantity=qty,
                                    price=Decimal(str(item.get("discounted_price", 0))),
                                    original_price=Decimal(str(item.get("original_price", 0))),
                                    discount_amount=Decimal(str(item.get("product_discount", 0) or 0)),
                                )
                                
                                product.stock -= qty
                                product.save()
                                logger.info(f"📉 Остаток обновлен: товар={product.id}, новый_остаток={product.stock}")
                            else:
                                logger.warning(f"⚠️ Недостаточно остатка для товара {product_id}")
                                
                        except Product.DoesNotExist:
                            logger.error(f"❌ Товар не найден: {product_id}")
                            continue

                    logger.info(f"🎉 Заказ {order.id} успешно создан с позициями")

                # 🔹 КОРЗИНУ ОЧИСТКА ЧЕРЕЗ SESSION MODEL
                try:
                    if payment.session_key:
                        logger.info(f"🔄 Попытка очистки корзины для session_key: {payment.session_key}")
                        
                        from django.contrib.sessions.models import Session
                        try:
                            session = Session.objects.get(session_key=payment.session_key)
                            session_data = session.get_decoded()
                            
                            cart_session_id = 'cart'  # Убедитесь что это совпадает с CART_SESSION_ID
                            
                            logger.info(f"📋 Session keys до очистки: {list(session_data.keys())}")
                            
                            if cart_session_id in session_data:
                                cart_before = session_data[cart_session_id]
                                logger.info(f"🛒 Корзина до очистки: {cart_before}")
                                
                                # Удаляем корзину
                                del session_data[cart_session_id]
                                
                                # Сохраняем обновленную сессию
                                session.session_data = Session.objects.encode(session_data)
                                session.save()
                                
                                logger.info(f"✅ Корзина очищена в callback для session {payment.session_key}")
                                
                                # Проверяем что действительно удалено
                                updated_session = Session.objects.get(session_key=payment.session_key)
                                updated_data = updated_session.get_decoded()
                                logger.info(f"📋 Session keys после очистки: {list(updated_data.keys())}")
                            else:
                                logger.info(f"ℹ️ Корзина уже очищена для session {payment.session_key}")
                                
                        except Session.DoesNotExist:
                            logger.warning(f"⚠️ Сессия не найдена в БД: {payment.session_key}")
                            
                except Exception as e:
                    logger.exception(f"❌ Ошибка очистки корзины в callback: {str(e)}")

        except Exception as e:
            logger.exception(f"❌ Ошибка создания заказа для платежа {payment.id}: {str(e)}")
            payment.status = "в обработке"
            payment.save()
            return HttpResponse("Ошибка создания заказа", status=500)

    elif status in failed_statuses:
        payment.status = "ошибка"
        payment.save()
        logger.info(f"❌ Платеж {payment.id} помечен как 'ошибка'")

    else:
        logger.info(f"ℹ️ Неизвестный статус '{status}' для платежа {payment.id}")

    logger.info("✅ Обработка callback завершена")
    return HttpResponse("OK")


def payment_success(request):
    """Когда платеж успешно завершен (страница, на которую попадает пользователь)"""
    logger.info("📩 Получен запрос на payment_success")
    logger.debug(f"Request GET params: {request.GET}")

    billing_id = request.GET.get('order_id')

    if billing_id:
        try:
            payment = Payment.objects.get(billing_id=billing_id)
            logger.info(f"➡️ Просмотр success для payment {payment.id}")
            
            # 🔹 КОРЗИНУ ОЧИСТКА - ИСПОЛЬЗУЕМ Cart CLASS
            try:
                cart = Cart(request)
                cart_items_count = len(cart)
                
                if cart_items_count > 0:
                    logger.info(f"🛒 Корзина до очистки: {cart_items_count} товаров")
                    
                    # Используем метод clear() из Cart класса
                    cart.clear()
                    
                    # Проверяем что корзина действительно очищена
                    cart_after = Cart(request)
                    logger.info(f"✅ Корзина очищена в success view. После: {len(cart_after)} товаров")
                else:
                    logger.info(f"ℹ️ Корзина уже пуста в success view")
                    
            except Exception as e:
                logger.exception(f"❌ Ошибка очистки корзины в success view: {str(e)}")
            
            try:
                # Ищем заказ по payment_id
                order = Order.objects.get(payment_id=payment.billing_id)
                context = {
                    'order': order,
                    'payment': payment
                }
            except Order.DoesNotExist:
                logger.info(f"⚠️ Заказ ещё не создан для payment {payment.id}")
                context = {
                    'payment': payment,
                    'message': 'Заказ еще обрабатывается'
                }
        except Payment.DoesNotExist:
            logger.error(f"❌ Payment не найден для billing_id={billing_id} в success view")
            context = {
                'message': 'Данные платежа не найдены'
            }
    else:
        logger.warning("⚠️ В success view не передан order_id")
        # Har holda cartni tozalaymiz
        try:
            cart = Cart(request)
            if len(cart) > 0:
                cart.clear()
                logger.info("✅ Корзина очищена в success view (без order_id)")
        except:
            pass
            
        context = {
            'message': 'Оплата прошла успешно'
        }

    return render(request, 'payment/success.html', context)


def payment_failed(request):
    """Когда платеж завершен неудачно"""
    logger.info("📩 Получен запрос на payment_failed")
    logger.debug(f"Request GET params: {request.GET}")

    billing_id = request.GET.get('order_id')

    context = {}
    if billing_id:
        try:
            payment = Payment.objects.get(billing_id=billing_id)
            payment.status = 'ошибка'
            payment.save()
            logger.info(f"❌ Payment {payment.id} помечен как 'ошибка' из failed view")
            context['payment'] = payment
        except Payment.DoesNotExist:
            logger.error(f"❌ Payment не найден для billing_id={billing_id} в failed view")
    else:
        logger.warning("⚠️ В failed view не передан order_id")
        context['message'] = 'Ошибка оплаты'

    return render(request, 'payment/fail.html', context)
