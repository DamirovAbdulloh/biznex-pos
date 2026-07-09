from django.db import models
from syncing.mixins import SyncModel

class Role(SyncModel):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Employee(SyncModel):
    name = models.CharField(max_length=200)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    pin_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0,
        help_text="Buyurtma summasidan oladigan foizi (%)")
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0,
        help_text="Kunlik ish haqi (UZS)")
    monthly_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0,
        help_text="Oylik ish haqi (UZS)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_initials(self):
        parts = self.name.split()
        return ''.join([p[0].upper() for p in parts[:2]])
    
    def get_daily_earnings(self, date=None):
        """Xodimning kunlik ish haqi (komissiya + kunlik stavka).
        Saboy (mijoz o'zi olib ketgan) buyurtmalardan komissiya olinmaydi."""
        from django.utils import timezone
        from orders.models import Order
        from django.db.models import Sum
        if date is None:
            date = timezone.now().date()
        closed_orders = Order.objects.filter(
            employee=self, status='closed', created_at__date=date, is_takeaway=False
        )
        total_sales = sum(o.get_total() for o in closed_orders)
        commission = total_sales * self.commission_percent / 100
        return self.daily_rate + commission, total_sales, commission
    
    def get_monthly_earnings(self, year=None, month=None):
        """Xodimning oylik ish haqi.
        Saboy (mijoz o'zi olib ketgan) buyurtmalardan komissiya olinmaydi."""
        from django.utils import timezone
        from orders.models import Order
        now = timezone.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        closed_orders = Order.objects.filter(
            employee=self, status='closed',
            created_at__year=year, created_at__month=month, is_takeaway=False
        )
        total_sales = sum(o.get_total() for o in closed_orders)
        commission = total_sales * self.commission_percent / 100
        return self.monthly_rate + commission, total_sales, commission
