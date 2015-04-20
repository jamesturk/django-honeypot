import six

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps # Python <= 2.4

from django.conf import settings
from django.utils.safestring import mark_safe
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.template.loader import render_to_string

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
    redirect = getattr(settings, 'HONEYPOT_REDIRECT_URL', None)
    use_js_field = getattr(settings, 'HONEYPOT_USE_JS_FIELD', False)
    
    if request.method == 'POST':
        field = field_name or settings.HONEYPOT_FIELD_NAME
        js_field = field + '_js'
        
        failed_js_validation = False
        if use_js_field and js_field not in request.POST:
            failed_js_validation = True
        
        if field not in request.POST or not verifier(request.POST[field]) or failed_js_validation:
            
            #If a redirect url is specified in the settings, redirect user
            if redirect != None:
                return HttpResponseRedirect(redirect)
            
            resp = render_to_string('honeypot/honeypot_error.html',
                                {'fieldname': field})
            return HttpResponseBadRequest(resp)

def check_honeypot(func=None, field_name=None):
    """
        Check request.POST for valid honeypot field.

        Takes an optional field_name that defaults to HONEYPOT_FIELD_NAME if
        not specified.
    """
    # hack to reverse arguments if called with str param
    if isinstance(func, six.string_types):
        func, field_name = field_name, func

    def decorated(func):
        def inner(request, *args, **kwargs):
            response = verify_honeypot_value(request, field_name)
            if response:
                return response
            else:
                return func(request, *args, **kwargs)
        return wraps(func)(inner)

    if func is None:
        def decorator(func):
            return decorated(func)
        return decorator
    return decorated(func)
