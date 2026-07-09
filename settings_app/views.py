from django.conf import settings as dj_settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ReceiptSettings


def settings_view(request):
    settings_obj = ReceiptSettings.get_solo()

    if request.method == 'POST':
        settings_obj.paper_size = request.POST.get('paper_size', '80mm')
        try:
            settings_obj.custom_width_mm = int(request.POST.get('custom_width_mm') or 80)
        except ValueError:
            settings_obj.custom_width_mm = 80
        try:
            settings_obj.font_size_px = int(request.POST.get('font_size_px') or 13)
        except ValueError:
            settings_obj.font_size_px = 13
        try:
            settings_obj.print_scale_percent = int(request.POST.get('print_scale_percent') or 100)
        except ValueError:
            settings_obj.print_scale_percent = 100
        settings_obj.auto_print = request.POST.get('auto_print') == 'on'
        settings_obj.show_logo = request.POST.get('show_logo') == 'on'
        settings_obj.footer_text = request.POST.get('footer_text', '').strip()
        try:
            cols = int(request.POST.get('pos_grid_columns') or 3)
        except ValueError:
            cols = 3
        settings_obj.pos_grid_columns = max(2, min(cols, 6))
        settings_obj.save()
        messages.success(request, "Sozlamalar saqlandi")
        return redirect('settings_app:settings')

    sync_info = None
    if getattr(dj_settings, 'DESKTOP_MODE', False):
        sync_info = _get_sync_info()

    return render(request, 'settings_app/settings.html', {
        'settings': settings_obj,
        'paper_size_choices': ReceiptSettings.PAPER_SIZE_CHOICES,
        'active_page': 'settings',
        'sync_info': sync_info,
    })


def _get_sync_info():
    remote_url = getattr(dj_settings, 'SYNC_REMOTE_URL', '') or ''
    api_key = getattr(dj_settings, 'SYNC_API_KEY', '') or ''
    last_sync = ''
    try:
        from syncing.client import _load_state
        last_sync = _load_state().get('last_sync', '')
    except Exception:
        pass
    return {
        'configured': bool(remote_url and api_key),
        'remote_url': remote_url,
        'last_sync': last_sync,
    }


def sync_now_view(request):
    """Sozlamalar sahifasidan qo'lda sinxronlashni ishga tushirish (desktop rejimda)."""
    if request.method == 'POST' and getattr(dj_settings, 'DESKTOP_MODE', False):
        from syncing.client import sync_once
        remote_url = getattr(dj_settings, 'SYNC_REMOTE_URL', '') or ''
        api_key = getattr(dj_settings, 'SYNC_API_KEY', '') or ''
        if not remote_url or not api_key:
            messages.error(request, "Avval config.json faylida remote_url va sync_api_key to'ldiring")
        else:
            ok = sync_once(remote_url, api_key)
            if ok:
                messages.success(request, "Sinxronlash muvaffaqiyatli yakunlandi")
            else:
                messages.warning(request, "Sinxronlash amalga oshmadi — internet yo'q yoki sayt javob bermadi")
    return redirect('settings_app:settings')
