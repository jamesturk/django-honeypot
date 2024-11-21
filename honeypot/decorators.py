from functools import wraps

from django.conf import settings
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from django.urls import get_callable


def honeypot_equals(val):
    """
    Default verifier used if HONEYPOT_VERIFIER is not specified.
    Ensures val == HONEYPOT_VALUE or HONEYPOT_VALUE() if it's a callable.
    """
    expected = getattr(settings, "HONEYPOT_VALUE", "")
    if callable(expected):
        expected = expected()
    return val == expected


def honeypot_error(request, context):
    """
    Default responder used if HONEYPOT_RESPONDER is not specified.
    Return HttpResponseBadRequest for invalid honeypot.
    """
    resp = render_to_string(
        "honeypot/honeypot_error.html",
        context=context,
        request=request,
    )
    return HttpResponseBadRequest(resp)


def verify_honeypot_value(request, field_name):
    """
    Verify that request.POST[field_name] is a valid honeypot.

    Ensures that the field exists and passes verification according to
    HONEYPOT_VERIFIER.
    """
    verifier = getattr(settings, "HONEYPOT_VERIFIER", honeypot_equals)
    responder = getattr(settings, "HONEYPOT_RESPONDER", honeypot_error)
    responder = get_callable(responder)
    if request.method == "POST":
        field = field_name or settings.HONEYPOT_FIELD_NAME
        if field not in request.POST or not verifier(request.POST[field]):
            return responder(request, {"fieldname": field})
    return None


def check_honeypot(func=None, field_name=None):
    """
    Check request.POST for valid honeypot field.

    Takes an optional field_name that defaults to HONEYPOT_FIELD_NAME if
    not specified.
    """
    # hack to reverse arguments if called with str param
    if isinstance(func, str):
        func, field_name = field_name, func

    def decorated(func):
        def inner(request, *args, **kwargs):
            response = verify_honeypot_value(request, field_name)
            return response or func(request, *args, **kwargs)

        return wraps(func)(inner)

    if func is None:

        def decorator(func):
            return decorated(func)

        return decorator
    return decorated(func)


def honeypot_exempt(view_func):
    """
    Mark view as exempt from honeypot validation
    """

    # borrowing liberally from django's csrf_exempt
    def wrapped(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped.honeypot_exempt = True
    return wraps(view_func)(wrapped)
