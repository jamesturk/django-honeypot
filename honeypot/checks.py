from django.conf import settings
from django.core.checks import Error


def check_middleware_order(app_configs, **kwargs):
    middleware = list(settings.MIDDLEWARE)
    if "django.middleware.common.CommonMiddleware" not in middleware:
        return []

    if "honeypot.middleware.HoneypotMiddleware" in middleware:
        honeypot_index = middleware.index("honeypot.middleware.HoneypotMiddleware")
    elif "honeypot.middleware.HoneypotResponseMiddleware" in middleware:
        honeypot_index = middleware.index(
            "honeypot.middleware.HoneypotResponseMiddleware"
        )
    else:
        return []

    if honeypot_index < middleware.index("django.middleware.common.CommonMiddleware"):
        return [
            Error(
                "The honeypot middleware needs to be listed after CommonMiddleware",
                id="honeypot.E001",
            ),
        ]

    return []
