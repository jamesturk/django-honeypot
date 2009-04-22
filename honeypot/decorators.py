try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps # Python <= 2.4

from django.conf import settings
from django.http import HttpResponseBadRequest

def verify_honeypot_value(val):
    expected = getattr(settings, 'HONEYPOT_VALUE', '')
    if callable(expected):
        expected = callable()
    return val == expected

def check_honeypot(func=None, field_name=None):
    verifier = getattr(settings, 'HONEYPOT_VERIFIER', verify_honeypot_value)

    def inner(request, *args, **kwargs):
        if request.method == 'POST':
            field = field_name or settings.HONEYPOT_FIELD_NAME
            if field not in request.POST or not verifier(request.POST[field]):
                return HttpResponseBadRequest('Honeypot Error')
        return func(request, *args, **kwargs)
    inner = wraps(func)(inner)

    if func is None:
        def decorator(func):
            return inner
        return decorator
    return inner
