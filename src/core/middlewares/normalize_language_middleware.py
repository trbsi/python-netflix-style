from threading import settrace

from django.utils import translation

from automationapp import settings
from src.core.utils import get_ip_data


class NormalizeLanguageMiddleware:
    GEOIP_ENABLED=False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = translation.get_language_from_request(request)

        if lang and '-' in lang:
            lang = lang.split('-')[0]  # en-gb → en
        elif self.GEOIP_ENABLED:
            ip_data = get_ip_data(None,request)
            lang = ip_data.get_language()
        else:
            lang = settings.LANGUAGE_CODE

        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        return self.get_response(request)
