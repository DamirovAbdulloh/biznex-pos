from django.db import models
from syncing.mixins import SyncModel
from orders.models import Order
from employees.models import Employee

class Transaction(SyncModel):
    CATEGORY_CHOICES = [
        ('order', 'Buyurtma'),
        ('other', 'Boshqa'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Naqd pul'),
        ('card', 'Karta'),
        ('transfer', "O'tkazma"),
    ]
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    smena = models.ForeignKey('smena.Smena', on_delete=models.SET_NULL, null=True, blank=True, related_name='smena_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='order')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    note = models.CharField(max_length=300, blank=True)
    is_voided = models.BooleanField(default=False,
        help_text="Buyurtma o'chirilgani sababli bekor qilingan tranzaksiya — balansdan ayirilgan, "
                   "lekin tarix uchun saqlanadi")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"Tranzaksiya #{self.pk} - {self.amount} UZS"

    class Meta:
        ordering = ['-created_at']
