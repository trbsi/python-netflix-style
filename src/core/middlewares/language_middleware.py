from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class LanguageMiddleware(MiddlewareMixin):
    COOKIE_NAME = "site_language"

    def process_request(self, request):
        path = request.path_info.strip("/").split("/")

        url_lang = path[0] if len(path) > 0 else None

        supported_languages = self.get_supported_languages()

        language_code = None

        # 1. URL-based language (highest priority)
        if url_lang in supported_languages:
            language_code = url_lang

        # 2. Cookie fallback
        elif request.COOKIES.get(self.COOKIE_NAME) in supported_languages:
            language_code = request.COOKIES.get(self.COOKIE_NAME)

        # 3. Browser Accept-Language fallback
        else:
            language_code = self.get_browser_language(request, supported_languages)

        # 4. Final fallback to default language
        if not language_code:
            language_code = self.get_default_language()

        # attach to request
        request.LANGUAGE_CODE = language_code

        # activate translation system
        translation.activate(language_code)

    def process_response(self, request, response):
        language_code = getattr(request, "LANGUAGE_CODE", None)

        if language_code:
            response.set_cookie(
                self.COOKIE_NAME,
                language_code,
                max_age=60 * 60 * 24 * 365,  # 1 year
                samesite="Lax",
            )

        translation.deactivate()

        return response

    def get_supported_languages(self):
        return set(('en', 'es', 'de', 'hr', 'sr'))

    def get_default_language(self):
        return 'en'

    def get_browser_language(self, request, supported):
        accept = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
        for lang in accept.split(","):
            code = lang.split(";")[0].strip().lower()
            if code in supported:
                return code
        return None
