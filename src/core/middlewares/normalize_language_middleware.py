from django.conf import settings
from django.utils import translation

from src.core.utils.utils import get_ip_data


class NormalizeLanguageMiddleware:
    GEOIP_ENABLED = True

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Respect explicit user choice (cookie)
        lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

        # GEOIP fallback
        if not lang and self.GEOIP_ENABLED:
            ip_data = get_ip_data(None, request)
            lang = ip_data.get_language()

        # Normalize
        if lang and '-' in lang:
            lang = lang.split('-')[0]

        # Final fallback
        if not lang:
            lang = settings.LANGUAGE_CODE

        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        return self.get_response(request)
