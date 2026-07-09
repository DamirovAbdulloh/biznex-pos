from django.db import models
from syncing.mixins import SyncModel


class ReceiptSettings(SyncModel):
    """Chek chop etish sozlamalari — bitta yagona qator (singleton)"""
    PAPER_SIZE_CHOICES = [
        ('58mm', "58mm (kichik termal printer)"),
        ('80mm', "80mm (standart termal printer)"),
        ('A4', "A4 (oddiy printer)"),
        ('custom', "Boshqa (qo'lda kiritish)"),
    ]

    paper_size = models.CharField(max_length=20, choices=PAPER_SIZE_CHOICES, default='80mm')
    custom_width_mm = models.PositiveIntegerField(default=80, help_text="'Boshqa' tanlanganda chek kengligi (mm)")
    font_size_px = models.PositiveIntegerField(default=13, help_text="Asosiy matn shrift o'lchami (px)")
    print_scale_percent = models.PositiveIntegerField(default=100, help_text="Chop etish masштabi (%) — printer oynasidagi 'Масштаб'га mos")
    auto_print = models.BooleanField(default=True, help_text="To'lov tasdiqlangach chek avtomatik chop etilsin")
    show_logo = models.BooleanField(default=True)
    footer_text = models.CharField(
        max_length=255, blank=True,
        default="Xizmatimizdan foydalanganingiz uchun rahmat!\nYana tashrif buyuring"
    )
    pos_grid_columns = models.PositiveIntegerField(
        default=3, verbose_name="Taomlar panelidagi ustunlar soni",
        help_text="POS (buyurtma) ekranida bir qatorda nechta taom kartasi ko'rsatilsin (3-6)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chek sozlamasi"
        verbose_name_plural = "Chek sozlamalari"

    def __str__(self):
        return "Chek sozlamalari"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_width_mm(self):
        if self.paper_size == '58mm':
            return 58
        if self.paper_size == '80mm':
            return 80
        if self.paper_size == 'A4':
            return 210
        return self.custom_width_mm
