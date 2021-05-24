import re
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import force_str
from honeypot.decorators import verify_honeypot_value

# these were moved out of Django 1.2 -- we're going to still use them
_POST_FORM_RE = re.compile(
    r'(<form\W[^>]*\bmethod\s*=\s*(\'|"|)POST(\'|"|)\b[^>]*>)', re.IGNORECASE
)
_HTML_TYPES = ("text/html", "application/xhtml+xml")


class BaseHoneypotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


class HoneypotViewMiddleware(BaseHoneypotMiddleware):
    """
    Middleware that verifies a valid honeypot on all non-ajax POSTs.
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.is_ajax():
            return None
        if getattr(callback, "honeypot_exempt", False):
            return None
        return verify_honeypot_value(request, None)


class HoneypotResponseMiddleware(BaseHoneypotMiddleware):
    """
    Middleware that rewrites all POST forms to include honeypot field.
    """

    def __call__(self, request):
        response = self.get_response(request)

        try:
            content_type = response["Content-Type"].split(";")[0]
        except (KeyError, AttributeError):
            content_type = None

        if content_type in _HTML_TYPES:
            # ensure we don't add the 'id' attribute twice (HTML validity)
            def add_honeypot_field(match):
                """Returns the matched <form> tag plus the added <input> element"""
                value = getattr(settings, "HONEYPOT_VALUE", "")
                if callable(value):
                    value = value()
                return mark_safe(
                    match.group()
                    + render_to_string(
                        "honeypot/honeypot_field.html",
                        {"fieldname": settings.HONEYPOT_FIELD_NAME, "value": value},
                    )
                )

            # Modify any POST forms
            response.content = _POST_FORM_RE.sub(
                add_honeypot_field, force_str(response.content)
            )
        return response


class HoneypotMiddleware(HoneypotViewMiddleware, HoneypotResponseMiddleware):
    """
    Combines HoneypotViewMiddleware and HoneypotResponseMiddleware.
    """
