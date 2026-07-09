import datetime
import decimal
import uuid


def _to_json_safe(value):
    if isinstance(value, decimal.Decimal):
        return str(value)
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def _from_json_safe(field, value):
    if value is None:
        return None
    internal = field.get_internal_type()
    if internal == 'DecimalField':
        return decimal.Decimal(str(value))
    if internal == 'DateTimeField':
        from django.utils.dateparse import parse_datetime
        return parse_datetime(value)
    if internal == 'DateField':
        from django.utils.dateparse import parse_date
        return parse_date(value)
    return value


def serialize_instance(instance, fk_map):
    """Bitta model yozuvini JSON-safe dict'ga aylantiradi.
    FK maydonlari xom `id` o'rniga bog'langan obyektning `sync_id`si sifatida chiqadi."""
    data = {}
    for field in instance._meta.fields:
        name = field.name
        if name == 'id':
            continue
        if name in fk_map:
            related = getattr(instance, name)
            data[f"{name}_sync_id"] = str(related.sync_id) if related is not None else None
            continue
        data[name] = _to_json_safe(getattr(instance, name))
    return data


def serialize_queryset(queryset, fk_map):
    return [serialize_instance(obj, fk_map) for obj in queryset]


def apply_record(model, fk_map, record):
    """Bitta kelgan yozuvni (record) mahalliy/masofaviy bazaga upsert qiladi.
    Qaytaradi: 'applied' | 'skipped_stale' | 'deferred' (bog'langan obyekt hali yo'q)."""
    from django.utils.dateparse import parse_datetime

    sync_id = record.get('sync_id')
    if not sync_id:
        return 'skipped_stale'

    incoming_updated = parse_datetime(record.get('sync_updated_at')) if record.get('sync_updated_at') else None

    try:
        instance = model.objects.get(sync_id=sync_id)
        is_new = False
    except model.DoesNotExist:
        instance = model(sync_id=sync_id)
        is_new = True

    if not is_new and incoming_updated and instance.sync_updated_at and instance.sync_updated_at >= incoming_updated:
        # Mahalliy/mavjud yozuv allaqachon teng yoki yangiroq — o'zgartirmaymiz
        return 'skipped_stale'

    # Avval oddiy (FK bo'lmagan) maydonlarni qo'yamiz
    for field in model._meta.fields:
        name = field.name
        if name in ('id', 'sync_id'):
            continue
        if name in fk_map:
            continue
        if name in record:
            setattr(instance, name, _from_json_safe(field, record.get(name)))

    # FK maydonlarni sync_id orqali yechish
    for field_name, related_label in fk_map.items():
        key = f"{field_name}_sync_id"
        related_sync_id = record.get(key)
        if related_sync_id is None:
            setattr(instance, f"{field_name}_id", None)
            continue
        related_model = _resolve_model(related_label)
        try:
            related_obj = related_model.objects.get(sync_id=related_sync_id)
        except related_model.DoesNotExist:
            return 'deferred'
        setattr(instance, field_name, related_obj)

    instance.save(from_sync=True)
    return 'applied'


def _resolve_model(label):
    from django.apps import apps
    app_label, model_name = label.split('.')
    return apps.get_model(app_label, model_name)
