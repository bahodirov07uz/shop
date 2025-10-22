from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply the value by the arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def unique(value):
    """Ro‘yxat ichidagi unikal qiymatlarni qaytaradi"""
    if isinstance(value, list):
        return list(dict.fromkeys(value))
    return value
