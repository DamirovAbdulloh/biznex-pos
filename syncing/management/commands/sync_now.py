from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Saytga qo'lda bir martalik sinxronlash (push + pull) — sozlamalarni tekshirish uchun"

    def handle(self, *args, **options):
        from syncing.client import sync_once

        remote_url = getattr(settings, 'SYNC_REMOTE_URL', '') or ''
        api_key = getattr(settings, 'SYNC_API_KEY', '') or ''
        if not remote_url:
            self.stderr.write("SYNC_REMOTE_URL sozlanmagan (config.json yoki muhit o'zgaruvchisi orqali)")
            return
        if not api_key:
            self.stderr.write("SYNC_API_KEY sozlanmagan")
            return

        self.stdout.write(f"Sinxronlanmoqda: {remote_url} ...")
        ok = sync_once(remote_url, api_key)
        if ok:
            self.stdout.write(self.style.SUCCESS("Sinxronlash muvaffaqiyatli yakunlandi"))
        else:
            self.stdout.write(self.style.WARNING("Sinxronlash amalga oshmadi (internet yo'q yoki server xatosi)"))
