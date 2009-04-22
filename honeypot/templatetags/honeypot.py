from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('honeypot/honeypot_field.html')
def render_honeypot_field(field_name=None):
    if not field_name:
        field_name = settings.HONEYPOT_FIELD_NAME
    value = getattr(settings, 'HONEYPOT_VALUE', '')
    if callable(value):
        value = value()
    return {'fieldname': field_name, 'value': value}
