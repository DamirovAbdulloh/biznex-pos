from django.db import models
from syncing.mixins import SyncModel

class Category(SyncModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name
    
    @property
    def product_count(self):
        return self.product_set.count()
    
    class Meta:
        verbose_name_plural = "Kategoriyalar"

class Product(SyncModel):
    UNIT_CHOICES = [
        ('dona', 'Dona'),
        ('kg', 'Kilogram'),
        ('porsiya', 'Porsiya'),
        ('litr', 'Litr'),
    ]
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0,
        verbose_name="Sotish narxi", help_text="Mijozga sotiladigan narx (UZS)")
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0,
        verbose_name="Tan narxi", help_text="Taomning o'ziga tushgan narxi (UZS) — sof foydani hisoblash uchun")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='dona')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami",
        help_text="Taomlar ro'yxatida va POS panelida ko'rsatilish tartibi (kichigi birinchi)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Mahsulotlar"
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

    @property
    def profit_per_unit(self):
        """Bir dona/porsiya taomdan keladigan sof foyda"""
        return self.price - self.cost_price

    @property
    def profit_margin_percent(self):
        """Foyda marjasi foizda"""
        if self.price:
            return (self.profit_per_unit / self.price) * 100
        return 0

    def get_sales_stats(self, date_from=None, date_to=None):
        """Ushbu taomning sotuv statistikasi: qancha sotilgan, jami kirim, jami tan narx, sof foyda.
        Faqat to'langan (closed) buyurtmalardagi taomlar hisobga olinadi."""
        from orders.models import OrderItem
        items = OrderItem.objects.filter(product=self, order__status='closed')
        if date_from:
            items = items.filter(order__created_at__date__gte=date_from)
        if date_to:
            items = items.filter(order__created_at__date__lte=date_to)

        total_qty = sum(i.quantity for i in items)
        total_income = sum(i.get_subtotal() for i in items)
        total_cost = sum(i.quantity * self.cost_price for i in items)
        net_profit = total_income - total_cost

        return {
            'total_qty': total_qty,
            'total_income': total_income,
            'total_cost': total_cost,
            'net_profit': net_profit,
            'orders_count': items.values('order').distinct().count(),
        }
