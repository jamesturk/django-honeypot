try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps # Python <= 2.4

from django.conf import settings
from django.http import HttpResponseBadRequest

def check_honeypot(func=None, field_name=None):
    def inner(request, *args, **kwargs):
        if request.method == 'POST':
            field = field_name or settings.HONEYPOT_FIELD_NAME
            if field not in request.POST or request.POST[field] != '':
                return HttpResponseBadRequest('Honeypot Error')
        return func(request, *args, **kwargs)
    inner = wraps(func)(inner)

    if func is None:
        def decorator(func):
            return inner
        return decorator
    return inner
