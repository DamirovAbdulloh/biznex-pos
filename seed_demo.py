"""
Biznex — tozalash skripti
Loyihadagi BARCHA ma'lumotlarni o'chiradi (taomlar, kategoriyalar, buyurtmalar,
tranzaksiyalar, mijozlar, smenalar va boshqa xodimlar) va faqat bitta KASSIR
xodimini qoldiradi, ishni yangi (bo'sh) holatdan boshlash uchun.
"""
import os, sys, django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biznex.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.models import Role, Employee
from locations.models import Location, Table
from products.models import Category, Product
from clients.models import Client
from orders.models import Order, OrderItem
from transactions.models import Transaction
from smena.models import Smena

print("🗑️  Barcha ma'lumotlar o'chirilmoqda...")
OrderItem.objects.all().delete()
Order.objects.all().delete()
Transaction.objects.all().delete()
Smena.objects.all().delete()
Employee.objects.all().delete()
Role.objects.all().delete()
Product.objects.all().delete()
Category.objects.all().delete()
Table.objects.all().delete()
Location.objects.all().delete()
Client.objects.all().delete()
print("✅ Tozalandi\n")

# ===================== FAQAT BITTA KASSIR =====================
print("👤 Kassir yaratilmoqda...")
role_kassir = Role.objects.create(name='Kassir')
kassir = Employee.objects.create(
    name='Kassir',
    role=role_kassir,
    pin_code='1111',
    commission_percent=Decimal('0'),
    daily_rate=Decimal('0'),
    monthly_rate=Decimal('0'),
    phone='',
    is_active=True,
)
print(f"   1 ta xodim yaratildi: {kassir.name} (PIN: {kassir.pin_code})")

print("\n" + "=" * 50)
print("✅ LOYIHA TOZALANDI — FAQAT BITTA KASSIR QOLDI")
print("=" * 50)
print(f"  Lavozimlar:  {Role.objects.count()} ta")
print(f"  Xodimlar:    {Employee.objects.count()} ta")
print(f"  Joylar:      {Location.objects.count()} ta")
print(f"  Stollar:     {Table.objects.count()} ta")
print(f"  Kategoriya:  {Category.objects.count()} ta")
print(f"  Mahsulotlar: {Product.objects.count()} ta")
print(f"  Mijozlar:    {Client.objects.count()} ta")
print(f"  Buyurtmalar: {Order.objects.count()} ta")
print(f"  Tranzaksiya: {Transaction.objects.count()} ta")
print(f"  Smenalar:    {Smena.objects.count()} ta")
print()
print("🔑 Kassir PIN kodi: 1111")
print()
print("🌐 Ishga tushirish: python manage.py runserver")
