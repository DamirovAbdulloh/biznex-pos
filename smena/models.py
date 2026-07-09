from django.db import models
from django.utils import timezone
from syncing.mixins import SyncModel

class Smena(SyncModel):
    STATUS_CHOICES = [
        ('open', 'Ochiq'),
        ('closed', 'Yopiq'),
    ]
    opened_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Smena {self.opened_at.strftime('%d.%m.%Y')}"

    @property
    def total_sales(self):
        from transactions.models import Transaction
        return self.smena_transactions.filter(amount__gt=0).aggregate(
            s=models.Sum('amount'))['s'] or 0

    @property
    def total_returns(self):
        from transactions.models import Transaction
        return abs(self.smena_transactions.filter(amount__lt=0).aggregate(
            s=models.Sum('amount'))['s'] or 0)

    @property
    def net_income(self):
        return self.total_sales - self.total_returns

    class Meta:
        verbose_name = "Smena"
        verbose_name_plural = "Smenalar"
        ordering = ['-opened_at']
