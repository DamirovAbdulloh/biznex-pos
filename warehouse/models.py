from django.db import models
from syncing.mixins import SyncModel


class Balance(models.Model):
    """Restoran asosiy balansi (bitta yozuv)"""
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Balans"

    def __str__(self):
        return f"Balans: {self.amount} UZS"

    @classmethod
    def get_balance(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def add(cls, amount):
        from django.db.models import F
        cls.get_balance()  # mavjudligini ta'minlash
        cls.objects.filter(pk=1).update(amount=F('amount') + amount)
        return cls.objects.get(pk=1)

    @classmethod
    def subtract(cls, amount):
        from django.db.models import F
        cls.get_balance()
        cls.objects.filter(pk=1).update(amount=F('amount') - amount)
        return cls.objects.get(pk=1)


class WarehouseItem(SyncModel):
    """Omborga kiritilgan mahsulot (xarid)"""
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=1, verbose_name="Miqdori")
    unit = models.CharField(max_length=30, default="dona", verbose_name="O'lchov birligi")
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Birlik narxi")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Jami narx")
    note = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ombor mahsuloti"
        verbose_name_plural = "Ombor mahsulotlari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.total_cost} UZS"

    def save(self, *args, **kwargs):
        # Jami narxni hisoblash
        self.total_cost = self.quantity * self.price_per_unit
        is_new = self._state.adding
        super().save(*args, **kwargs)
        # Yangi yozuv bo'lsa balansdan ayir
        if is_new:
            Balance.subtract(self.total_cost)
