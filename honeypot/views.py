from honeypot.decorators import verify_honeypot_value


class HoneypotMixin(object):
    honeypot_fieldname = None

    def post(self, request, *args, **kwargs):
        from django.conf import settings
        honeypot_fieldname = self.honeypot_fieldname or getattr(settings,
                                                                'HONEYPOT_FIELD_NAME',
                                                                'family_name')
        response = verify_honeypot_value(request, honeypot_fieldname)
        if response:
            return response
        return super(HoneypotMixin, self).post(request, *args, **kwargs)
