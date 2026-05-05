import re

from django.conf import settings
from django.http import HttpRequest
from django.utils import translation

from automationapp import settings as app_settings
from src.core.utils.utils import get_ip_data


class NormalizeLanguageMiddleware:
    GEOIP_ENABLED = True

    BOT_PATTERNS = [
        r"bot",
        r"crawl",
        r"spider",
        r"slurp",
        r"facebookexternalhit",
        r"twitterbot",
        r"linkedinbot",
        r"preview",
        r"fetch",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # FORCE ENGLISH FOR BOTS
        if self.is_bot(request):
            lang = "en"
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
            return self.get_response(request)

        # Normal users
        # Respect explicit user choice (cookie)
        lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

        # GEOIP fallback
        if not lang and self.GEOIP_ENABLED:
            ip_data = get_ip_data(None, request)
            lang = ip_data.get_language()
            is_supported = any(lang == code for code, _ in app_settings.SUPPORTED_LANGUAGES)
            if not is_supported:
                lang = app_settings.LANGUAGE_CODE

        # Normalize
        if lang and '-' in lang:
            lang = lang.split('-')[0]

        # Final fallback
        if not lang:
            lang = app_settings.LANGUAGE_CODE

        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        return self.get_response(request)

    def is_bot(self, request: HttpRequest):
        user_agent = (request.META.get("HTTP_USER_AGENT") or "").lower()
        return any(re.search(pattern, user_agent) for pattern in self.BOT_PATTERNS)
