from django.core.management.base import BaseCommand
from django.utils import timezone
from asic.models import Order, OrderStatusRule

class Command(BaseCommand):
    help = "Автоматически обновляет статусы заказов по правилам"

    def handle(self, *args, **options):
        now = timezone.now()
        rules = OrderStatusRule.objects.filter(is_active=True).order_by("-days_after", "order_priority")

        self.stdout.write(f"🔍 Найдено {rules.count()} активных правил:")
        for rule in rules:
            self.stdout.write(f"   - {rule.days_after} дней → {rule.status}")

        updated_count = 0
        
        # ✅ Faqat "new", "processing", "ready", "shipped" statusidagi buyurtmalarni olamiz
        # ❌ "cancelled", "completed" larni olmaymiz
        orders = Order.objects.exclude(status__in=['cancelled', 'completed']).order_by("-created_at")

        self.stdout.write(f"🔍 Обрабатывается {orders.count()} заказов (исключая отмененные и завершенные)")

        for order in orders:
            # ✅ HAR DOIM created_at dan hisoblaymiz!
            reference_date = order.created_at
            days_passed = (now.date() - reference_date.date()).days

            self.stdout.write(
                f"🔍 Заказ {order.order_number}: "
                f"создан: {reference_date.date()}, "
                f"прошло {days_passed} дней, "
                f"текущий статус: {order.status}"
            )

            old_status = order.status
            new_status = None

            # ✅ Qoidalarni qo'llash - eng katta days_after dan boshlab
            for rule in rules:
                if days_passed >= rule.days_after:
                    new_status = rule.status
                    break

            # ✅ Status yangilash shartlari
            if new_status and new_status != old_status:
                order.status = new_status
                order.last_status_update = now
                order.save(update_fields=["status", "last_status_update"])
                self.stdout.write(
                    f"✅ Заказ {order.order_number}: {days_passed} дней → {new_status} (был: {old_status})"
                )
                updated_count += 1
            else:
                self.stdout.write(
                    f"➖ Заказ {order.order_number}: {days_passed} дней → без изменений ({old_status})"
                )

        self.stdout.write(self.style.SUCCESS(f"🎯 {updated_count} заказов обновлено"))
