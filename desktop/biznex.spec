# PyInstaller spec — Biznex POS desktop .exe
# Ishga tushirish: pyinstaller desktop/biznex.spec  (loyiha papkasining ildizidan)

import sys
from pathlib import Path

block_cipher = None
ROOT = Path(SPECPATH).resolve().parent  # biznex_v2/

DJANGO_APPS = [
    "biznex", "orders", "products", "employees", "reports", "locations",
    "transactions", "clients", "smena", "warehouse", "settings_app", "syncing",
]

datas = [
    (str(ROOT / "templates"), "biznex_v2/templates"),
    (str(ROOT / "static"), "biznex_v2/static"),
]
for app in DJANGO_APPS:
    app_dir = ROOT / app
    if app_dir.exists():
        datas.append((str(app_dir), f"biznex_v2/{app}"))

hiddenimports = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.template.context_processors",
    "whitenoise",
    "whitenoise.middleware",
    "whitenoise.storage",
    "whitenoise.responders",
    "whitenoise.string_utils",
    "whitenoise.media_types",
    "waitress",
    "requests",
]
for app in DJANGO_APPS:
    hiddenimports += [app, f"{app}.migrations"]

a = Analysis(
    [str(Path(SPECPATH) / "launcher.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="BiznexPOS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    onefile=True,
    icon=None,
)
