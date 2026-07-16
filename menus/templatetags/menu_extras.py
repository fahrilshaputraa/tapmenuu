from django import template

register = template.Library()


@register.filter
def rupiah(value):
    try:
        amount = int(value)
    except (TypeError, ValueError):
        amount = 0

    return f'Rp {amount:,}'.replace(',', '.')
