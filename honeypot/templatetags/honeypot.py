from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def render_honeypot_field(field_name=None):
    if not field_name:
        field_name = settings.HONEYPOT_FIELD_NAME
    value = getattr(settings, 'HONEYPOT_VALUE', '')
    return '''<div style="display: none;">
    <label for="%(fieldname)s">leave this field blank to prove your humanity</label>
    <input type="text" id="%(fieldname)s" name="%(fieldname)s" value="%(value)s" />
    </div>''' % {'fieldname': field_name, 'value': value}
