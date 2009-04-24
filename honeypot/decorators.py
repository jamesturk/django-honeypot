try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps # Python <= 2.4

from django.conf import settings
from django.utils.safestring import mark_safe
from django.http import HttpResponseBadRequest

_ERROR_MSG = mark_safe('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"><body><h1>400 Bad Request</h1><p>Honey Pot Error. Request aborted.</p></body></html>')

def honeypot_equals(val):
    """
        Default verifier used if HONEYPOT_VERIFIER is not specified.
        Ensures val == HONEYPOT_VALUE or HONEYPOT_VALUE() if it's a callable.
    """
    expected = getattr(settings, 'HONEYPOT_VALUE', '')
    if callable(expected):
        expected = expected()
    return val == expected

def verify_honeypot_value(request, field_name):
    """
        Verify that request.POST[field_name] is a valid honeypot.

        Ensures that the field exists and passes verification according to
        HONEYPOT_VERIFIER.
    """
    verifier = getattr(settings, 'HONEYPOT_VERIFIER', honeypot_equals)
    if request.method == 'POST':
        field = field_name or settings.HONEYPOT_FIELD_NAME
        if field not in request.POST or not verifier(request.POST[field]):
            return HttpResponseBadRequest(_ERROR_MSG)

def check_honeypot(func=None, field_name=None):
    """
        Check request.POST for valid honeypot field.

        Takes an optional field_name that defaults to HONEYPOT_FIELD_NAME if
        not specified.
    """
    def inner(request, *args, **kwargs):
        response = verify_honeypot_value(request, field_name)
        if response:
            return response
        else:
            return func(request, *args, **kwargs)
    inner = wraps(func)(inner)

    if func is None:
        def decorator(func):
            return inner
        return decorator
    return inner
