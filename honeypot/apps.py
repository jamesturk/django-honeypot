from django.apps import AppConfig
from django.core import checks

from honeypot.checks import check_middleware_order


class HoneypotConfig(AppConfig):
    name = "honeypot"

    def ready(self):
        checks.register(check_middleware_order)
