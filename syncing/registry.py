"""
Sinxronlanadigan modellar reyestri.

Tartib MUHIM: ro'yxat "mustaqil" (FK'ga ega bo'lmagan yoki faqat oldingi
yozuvlarga bog'liq) modellardan boshlab, ularga bog'liq (FK orqali ishora
qiluvchi) modellar bilan tugaydi. Pull/push shu tartibda bajariladi —
shunda masalan Order sinxronlanganda unga bog'liq Table/Employee allaqachon
mavjud bo'ladi.

Har bir yozuv:
  "app_label.ModelName": {
      "fk": {"model_field_name": "app_label.RelatedModelName", ...}
  }
"""

SYNC_REGISTRY = [
    ("products", "Category", {}),
    ("employees", "Role", {}),
    ("locations", "Location", {}),
    ("clients", "Client", {}),
    ("settings_app", "ReceiptSettings", {}),
    ("products", "Product", {"category": "products.Category"}),
    ("employees", "Employee", {"role": "employees.Role"}),
    ("locations", "Table", {"location": "locations.Location"}),
    ("smena", "Smena", {}),
    ("orders", "Order", {"table": "locations.Table", "employee": "employees.Employee"}),
    ("orders", "OrderItem", {"order": "orders.Order", "product": "products.Product"}),
    ("transactions", "Transaction", {
        "order": "orders.Order", "employee": "employees.Employee", "smena": "smena.Smena",
    }),
    ("warehouse", "WarehouseItem", {}),
]


def get_model(app_label, model_name):
    from django.apps import apps
    return apps.get_model(app_label, model_name)
