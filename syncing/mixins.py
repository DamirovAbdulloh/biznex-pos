"""
SyncModel — mahalliy (desktop) va masofaviy (sayt/Railway) bazalar orasida
ma'lumotlarni sinxronlash uchun umumiy abstrakt model.

Har bir sinxronlanadigan model quyidagilarga ega bo'ladi:
- sync_id: ikkala baza uchun ham noyob bo'lgan UUID. PK (id) lar har bir bazada
  mustaqil ravishda beriladigan bo'lgani uchun (masalan mahalliy Order#5 va
  saytdagi Order#5 ikki xil yozuv bo'lishi mumkin), sinxronlash faqat shu
  sync_id orqali amalga oshiriladi — hech qachon xom `id` orqali emas.
- sync_updated_at: yozuv oxirgi marta o'zgargan vaqt — "kim oxirgi marta
  o'zgartirgan, o'sha g'olib" (last-write-wins) qoidasi shu maydon asosida
  ishlaydi.
- sync_deleted: "soft delete" belgisi — o'chirilgan yozuv butunlay
  o'chirilmaydi, faqat belgilanadi va shu holat boshqa tomonga ham sinxronlanadi.
- sync_dirty: True bo'lsa — bu yozuv hali narigi tomonga yuborilmagan
  ("push" qilinishi kerak). Push muvaffaqiyatli bo'lgach False bo'ladi.
"""
import uuid
from django.db import models


class SyncModel(models.Model):
    sync_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    sync_updated_at = models.DateTimeField(auto_now=True, db_index=True)
    sync_deleted = models.BooleanField(default=False, db_index=True)
    sync_dirty = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, from_sync=False, **kwargs):
        """from_sync=True — bu yozuv narigi tomondan sinxronlash orqali
        kelayotganini bildiradi, shuning uchun uni yana "dirty" (yuborilishi
        kerak) deb belgilamaymiz — aks holda cheksiz push/pull tsikli hosil bo'lardi."""
        self.sync_dirty = not from_sync
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.sync_deleted = True
        self.save()
