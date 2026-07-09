"""
Biznex POS — Desktop launcher.

Bu skript:
1. Django serverini (waitress orqali) fon rejimida, foydalanuvchi kompyuterida
   mahalliy (localhost) portda ishga tushiradi.
2. Birinchi marta ishga tushganda avtomatik migratsiyalarni bajaradi.
3. Native oyna (pywebview) ochib, o'sha localhost manzilini ko'rsatadi —
   natijada foydalanuvchi uchun oddiy desktop dastur bo'lib ko'rinadi.

PyInstaller bilan .exe qilib yig'ish uchun build.bat skriptidan foydalaning.
"""
import os
import sys
import socket
import threading
import time
import json
from pathlib import Path


def get_data_dir() -> Path:
    """Ma'lumotlar (baza, statik fayllar) saqlanadigan papka.
    .exe yonida emas, foydalanuvchi profilida saqlanadi — shunda dastur
    C:\\Program Files kabi yozish huquqi bo'lmagan joyga o'rnatilsa ham ishlayveradi."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".local" / "share"
    data_dir = base / "Biznex"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def exe_dir() -> Path:
    """.exe fayl joylashgan papka (config.json shu yerdan o'qiladi)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def load_config() -> dict:
    """config.json faylini .exe yonidan o'qiydi. Fayl bo'lmasa, standart
    (bo'sh) konfiguratsiya qaytariladi va namuna fayl yaratib qo'yiladi.

    remote_url — ENDI sahifani ko'rsatish uchun EMAS, faqat fon rejimida
    saytga sinxronlash (push/pull) uchun ishlatiladi. Dastur har doim
    mahalliy serverni ishga tushiradi va shu mahalliy oynani ko'rsatadi —
    shu tufayli internet bo'lmaganda ham hech qanday xatosiz ishlayveradi.
    """
    cfg_path = exe_dir() / "config.json"
    default = {"remote_url": "", "sync_api_key": ""}
    if not cfg_path.exists():
        try:
            cfg_path.write_text(json.dumps(default, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        return default
    try:
        return {**default, **json.loads(cfg_path.read_text(encoding="utf-8"))}
    except Exception:
        return default


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def resource_path(relative: str) -> str:
    """PyInstaller bilan yig'ilganda (--onefile) fayllar vaqtinchalik papkaga
    ochiladi (sys._MEIPASS); oddiy ishga tushirishda esa joriy papka ishlatiladi."""
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
    return str(Path(base) / relative)


def main():
    config = load_config()
    remote_url = (config.get("remote_url") or "").strip()
    sync_api_key = (config.get("sync_api_key") or "").strip()

    # Chekni hech qanday chop etish oynasi chiqmasdan, to'g'ridan-to'g'ri standart
    # printerga yuborish uchun (WebView2/Edge uchun ishlaydi — Windows desktop rejimida)
    os.environ.setdefault("WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS", "--kiosk-printing")

    import webview

    # --- Har doim mahalliy rejim: internet/server bo'lmaganda ham dastur to'liq,
    # xatosiz ishlashi shart. remote_url faqat pastroqda fon-sinxronlash uchun ishlatiladi. ---
    data_dir = get_data_dir()

    os.environ["BIZNEX_DESKTOP"] = "1"
    os.environ["BIZNEX_DATA_DIR"] = str(data_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biznex.settings")
    if remote_url:
        os.environ["SYNC_REMOTE_URL"] = remote_url
    if sync_api_key:
        os.environ["SYNC_API_KEY"] = sync_api_key

    project_root = resource_path("biznex_v2") if getattr(sys, "frozen", False) else str(
        Path(__file__).resolve().parent.parent
    )
    sys.path.insert(0, project_root)

    import django
    django.setup()

    # Birinchi ishga tushirishda (yoki yangilanishdan keyin) migratsiyalarni bajarish
    from django.core.management import call_command
    call_command("migrate", interactive=False, verbosity=0)
    try:
        call_command("collectstatic", interactive=False, verbosity=0)
    except Exception:
        pass  # static fayllar allaqachon yig'ilgan bo'lishi mumkin

    # Fon rejimida saytga sinxronlash — internet bo'lsa avtomatik ishlaydi,
    # bo'lmasa sukut bilan o'tkazib yuboriladi (dastur ishini to'xtatmaydi)
    if remote_url and sync_api_key:
        try:
            from syncing.client import start_background_sync
            start_background_sync(remote_url, sync_api_key)
        except Exception:
            pass  # sinxronlash ishga tushmasa ham, mahalliy dastur ishlashda davom etadi

    from biznex.wsgi import application
    from waitress import serve

    port = get_free_port()
    url = f"http://127.0.0.1:{port}/"

    server_thread = threading.Thread(
        target=lambda: serve(application, host="127.0.0.1", port=port, threads=8),
        daemon=True,
    )
    server_thread.start()

    # Server ochilishini biroz kutamiz
    time.sleep(1.2)

    webview.create_window("Biznex POS", url, width=1360, height=860, min_size=(1024, 640))
    webview.start()


if __name__ == "__main__":
    main()
