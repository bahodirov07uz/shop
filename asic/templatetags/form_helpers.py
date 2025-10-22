from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})



@register.filter
def get_delivery_rate(code, delivery_settings):
    if code == 'air':
        return delivery_settings.air_delivery_rate
    elif code == 'sea':
        return delivery_settings.sea_delivery_rate
    elif code == 'auto':
        return delivery_settings.auto_delivery_rate
    return 0

@register.filter
def get_document_percentage(code, delivery_settings):
    if code == 'gtd_rb':
        return delivery_settings.gtd_rb_cost
    elif code == 'dt_rf':
        return delivery_settings.dt_rf_cost
    return 0
