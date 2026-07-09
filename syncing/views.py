import json

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .registry import SYNC_REGISTRY, get_model
from .serializers import serialize_queryset, apply_record


def _check_key(request):
    key = request.headers.get('X-Sync-Key', '')
    expected = getattr(settings, 'SYNC_API_KEY', '')
    return bool(expected) and key == expected


@csrf_exempt
@require_http_methods(["GET"])
def sync_pull(request):
    """Ushbu server(saytda)dagi `since` vaqtidan keyin o'zgargan barcha
    yozuvlarni qaytaradi. Desktop ilova bularni o'ziga qo'llaydi (apply)."""
    if not _check_key(request):
        return JsonResponse({"error": "invalid_key"}, status=401)

    since_str = request.GET.get('since', '')
    since = None
    if since_str:
        from django.utils.dateparse import parse_datetime
        since = parse_datetime(since_str)

    server_time = timezone.now()
    result = {}
    for app_label, model_name, fk_map in SYNC_REGISTRY:
        model = get_model(app_label, model_name)
        qs = model.objects.all()
        if since:
            qs = qs.filter(sync_updated_at__gt=since)
        result[f"{app_label}.{model_name}"] = serialize_queryset(qs, fk_map)

    return JsonResponse({
        "server_time": server_time.isoformat(),
        "models": result,
    })


@csrf_exempt
@require_http_methods(["POST"])
def sync_push(request):
    """Desktop ilovadan kelgan "dirty" (hali yuborilmagan) yozuvlarni
    ushbu (saytdagi) bazaga qo'llaydi (upsert, sync_id orqali)."""
    if not _check_key(request):
        return JsonResponse({"error": "invalid_key"}, status=401)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid_json"}, status=400)

    incoming_models = body.get('models', {})
    results = {}
    for app_label, model_name, fk_map in SYNC_REGISTRY:
        key = f"{app_label}.{model_name}"
        records = incoming_models.get(key, [])
        if not records:
            continue
        model = get_model(app_label, model_name)
        counts = {"applied": 0, "skipped_stale": 0, "deferred": 0}
        applied_ids, deferred_ids = [], []
        for record in records:
            status = apply_record(model, fk_map, record)
            counts[status] = counts.get(status, 0) + 1
            if status in ('applied', 'skipped_stale'):
                applied_ids.append(record.get('sync_id'))
            elif status == 'deferred':
                deferred_ids.append(record.get('sync_id'))
        results[key] = {**counts, "applied_ids": applied_ids, "deferred_ids": deferred_ids}

    return JsonResponse({"results": results, "server_time": timezone.now().isoformat()})
