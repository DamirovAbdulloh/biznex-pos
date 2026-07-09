from django.db import models
from syncing.mixins import SyncModel
from locations.models import Table
from employees.models import Employee
from products.models import Product


class Order(SyncModel):
    STATUS_CHOICES = [
        ('open', 'Ochiq'),
        ('closed', 'Yopiq'),
        ('cancelled', 'Bekor'),
        ('deleted', "O'chirilgan"),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Naqd pul'),
        ('card', 'Karta'),
        ('transfer', "O'tkazma"),
    ]
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', db_index=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    sent_to_kitchen = models.BooleanField(default=False)
    kitchen_sent_at = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    is_takeaway = models.BooleanField(default=False, verbose_name="Saboy",
        help_text="Mijoz o'zi kelib oldi (saboy) — bu holatda xodimga komissiya hisoblanmaydi")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True,
        help_text="Buyurtma admin tomonidan o'chirilgan vaqt (agar o'chirilgan bo'lsa)")

    def __str__(self):
        if self.is_takeaway:
            return f"Saboy buyurtma #{self.pk}"
        return f"Buyurtma #{self.pk}"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.orderitem_set.all())

    def get_cost_total(self):
        """Buyurtmadagi barcha taomlarning jami tan narxi"""
        return sum(item.quantity * item.product.cost_price for item in self.orderitem_set.select_related('product').all())

    def get_net_profit(self):
        """Buyurtmaning sof foydasi (sotish narxi - tan narx)"""
        return self.get_total() - self.get_cost_total()

    def is_kitchen_expired(self):
        """20 daqiqadan o'tgan bo'lsa True"""
        if not self.kitchen_sent_at:
            return False
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.kitchen_sent_at + timedelta(minutes=20)


class OrderItem(SyncModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def get_subtotal(self):
        return self.quantity * self.price
