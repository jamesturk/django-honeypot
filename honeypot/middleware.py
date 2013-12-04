import re
import itertools
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.conf import settings
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from honeypot.decorators import verify_honeypot_value

# these were moved out of Django 1.2 -- we're going to still use them
_POST_FORM_RE = re.compile(r'(<form\W[^>]*\bmethod\s*=\s*(\'|"|)POST(\'|"|)\b[^>]*>)',
                           re.IGNORECASE)
_HTML_TYPES = ('text/html', 'application/xhtml+xml')

class HoneypotViewMiddleware(object):
    """
        Middleware that verifies a valid honeypot on all non-ajax POSTs.
    """
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.is_ajax():
            return None
        return verify_honeypot_value(request, None)

class HoneypotResponseMiddleware(object):
    """
        Middleware that rewrites all POST forms to include honeypot field.

        Borrows heavily from pre-Django 1.2 django.contrib.csrf.middleware.CsrfResponseMiddleware.
    """
    def process_response(self, request, response):

        if response['Content-Type'].split(';')[0] in _HTML_TYPES:
             # ensure we don't add the 'id' attribute twice (HTML validity)
            def add_honeypot_field(match):
                """Returns the matched <form> tag plus the added <input> element"""
                value = getattr(settings, 'HONEYPOT_VALUE', '')
                if callable(value):
                    value = value()
                return mark_safe(match.group() +
                                 render_to_string('honeypot/honeypot_field.html',
                                                  {'fieldname': settings.HONEYPOT_FIELD_NAME,
                                                   'value': value}))

            # Modify any POST forms
            response.content = _POST_FORM_RE.sub(add_honeypot_field, force_text(response.content))
        return response

class HoneypotMiddleware(HoneypotViewMiddleware, HoneypotResponseMiddleware):
    """
        Combines HoneypotViewMiddleware and HoneypotResponseMiddleware.
    """
    pass
