from django.db import models
from syncing.mixins import SyncModel

class Client(SyncModel):
    name = models.CharField(max_length=200, verbose_name="Ism")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    address = models.CharField(max_length=300, blank=True, verbose_name="Manzil")
    note = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"
        ordering = ['-created_at']
