from django import template

register = template.Library()


@register.filter(name='money')
def money(value, decimals=0):
    """Pul summasini har doim vergul bilan minglik ajratib formatlaydi: 273000 -> 273,000
    Django'ning standart intcomma filtri 'uz' locale'da probel ishlatadi,
    shu sababli bu maxsus filtr ishlatiladi."""
    try:
        decimals = int(decimals)
        value = float(value)
    except (TypeError, ValueError):
        return value
    formatted = f"{value:,.{decimals}f}"
    if decimals == 0:
        formatted = formatted.split('.')[0]
    return formatted
