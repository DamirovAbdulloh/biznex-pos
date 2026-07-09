"""
Desktop (.exe) tomonida ishlaydigan sinxronlash klienti.

Ishlash tartibi (har bir tsiklda):
1. Internet bor-yo'qligini tekshiradi (saytga qisqa so'rov).
2. Yo'q bo'lsa — hech narsa qilmaydi, xatosiz davom etadi (offline-first).
3. Bor bo'lsa:
   a. PUSH — mahalliy "dirty" (hali yuborilmagan) yozuvlarni saytga yuboradi.
   b. PULL — saytda oxirgi sinxronlashdan beri o'zgargan yozuvlarni oladi
      va mahalliyga qo'llaydi.
   c. Oxirgi muvaffaqiyatli sinxronlash vaqtini saqlaydi.

Muhim: bu butunlay fon (background) jarayon — foydalanuvchi interfeysini
hech qachon internetga bog'lab qo'ymaydi. Sayt yopiq/internet yo'q bo'lsa,
dastur to'liq mahalliy bazada, hech qanday xatosiz ishlashda davom etadi.
"""
import json
import logging
import threading
import time
from pathlib import Path

logger = logging.getLogger('syncing')

SYNC_TIMEOUT = 8  # soniya — sekin internetda ham osilib qolmasligi uchun
SYNC_INTERVAL = 45  # soniya — necha soniyada bir marta urinish


def _state_path():
    from django.conf import settings
    d = Path(settings.DATA_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d / 'sync_state.json'


def _load_state():
    p = _state_path()
    if not p.exists():
        return {"last_sync": ""}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {"last_sync": ""}


def _save_state(state):
    try:
        _state_path().write_text(json.dumps(state), encoding='utf-8')
    except Exception:
        logger.exception("sync_state saqlanmadi")


def has_internet(remote_url, timeout=4):
    import requests
    try:
        requests.get(remote_url.rstrip('/') + '/', timeout=timeout)
        return True
    except Exception:
        return False


def push_changes(remote_url, api_key):
    import requests
    from .registry import SYNC_REGISTRY, get_model
    from .serializers import serialize_instance

    payload_models = {}
    dirty_objects = {}  # key -> list of model instances (sync_id larini keyin dirty=False qilish uchun)
    for app_label, model_name, fk_map in SYNC_REGISTRY:
        model = get_model(app_label, model_name)
        qs = list(model.objects.filter(sync_dirty=True))
        if not qs:
            continue
        key = f"{app_label}.{model_name}"
        payload_models[key] = [serialize_instance(obj, fk_map) for obj in qs]
        dirty_objects[key] = {str(obj.sync_id): obj for obj in qs}

    if not payload_models:
        return

    resp = requests.post(
        remote_url.rstrip('/') + '/sync/push/',
        json={"models": payload_models},
        headers={"X-Sync-Key": api_key},
        timeout=SYNC_TIMEOUT,
    )
    resp.raise_for_status()
    results = resp.json().get('results', {})

    for key, objs_by_id in dirty_objects.items():
        applied_ids = set(results.get(key, {}).get('applied_ids', []))
        for sid, obj in objs_by_id.items():
            if sid in applied_ids:
                type(obj).objects.filter(pk=obj.pk).update(sync_dirty=False)


def pull_changes(remote_url, api_key):
    import requests
    from .registry import SYNC_REGISTRY, get_model
    from .serializers import apply_record

    state = _load_state()
    since = state.get('last_sync', '')

    resp = requests.get(
        remote_url.rstrip('/') + '/sync/pull/',
        params={"since": since},
        headers={"X-Sync-Key": api_key},
        timeout=SYNC_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    server_time = data.get('server_time')
    models_data = data.get('models', {})

    # Reyestr tartibida qo'llaymiz — mustaqil modellar avval, bog'liqlar keyin
    for app_label, model_name, fk_map in SYNC_REGISTRY:
        key = f"{app_label}.{model_name}"
        records = models_data.get(key, [])
        if not records:
            continue
        model = get_model(app_label, model_name)
        for record in records:
            apply_record(model, fk_map, record)

    if server_time:
        state['last_sync'] = server_time
        _save_state(state)


def sync_once(remote_url, api_key):
    if not remote_url or not api_key:
        return False
    if not has_internet(remote_url):
        return False
    try:
        push_changes(remote_url, api_key)
        pull_changes(remote_url, api_key)
        return True
    except Exception:
        logger.exception("Sinxronlashda xatolik (internet uzilgan yoki server javob bermadi)")
        return False


def start_background_sync(remote_url, api_key):
    """Fon oqimida davomiy sinxronlashni ishga tushiradi. Hech qachon
    dastur oynasini yoki foydalanuvchi ishini to'xtatib qo'ymaydi."""
    if not remote_url or not api_key:
        return

    def loop():
        # Dastur ochilishi bilanoq bir marta darhol urinib ko'ramiz
        time.sleep(3)
        while True:
            sync_once(remote_url, api_key)
            time.sleep(SYNC_INTERVAL)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
