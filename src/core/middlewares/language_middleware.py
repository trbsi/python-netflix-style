from django.utils import translation


class LanguageMiddleware:
    COOKIE_NAME = "site_language"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # --- process_request equivalent ---
        path_parts = [p for p in request.path_info.strip("/").split("/") if p]
        url_lang = path_parts[0] if path_parts else None

        supported_languages = self.get_supported_languages()
        language_code = None

        # 1. URL-based language
        if url_lang in supported_languages:
            language_code = url_lang

        # 2. Cookie fallback
        elif request.COOKIES.get(self.COOKIE_NAME) in supported_languages:
            language_code = request.COOKIES.get(self.COOKIE_NAME)

        # 3. Browser fallback
        else:
            language_code = self.get_browser_language(request, supported_languages)

        # 4. Default fallback
        if not language_code:
            language_code = self.get_default_language()

        # Activate language
        request.LANGUAGE_CODE = language_code
        translation.activate(language_code)

        # --- get response ---
        response = self.get_response(request)

        # --- process_response equivalent ---
        if language_code:
            response.set_cookie(
                self.COOKIE_NAME,
                language_code,
                max_age=60 * 60 * 24 * 365,
                samesite="Lax",
            )
            response["Content-Language"] = language_code

        translation.deactivate()

        return response

    def get_supported_languages(self):
        return {"en", "es", "de", "hr", "sr"}

    def get_default_language(self):
        return "en"

    def get_browser_language(self, request, supported):
        accept = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
        for lang in accept.split(","):
            code = lang.split(";")[0].strip().lower()
            code = code.split("-")[0]  # normalize (en-US → en)
            if code in supported:
                return code
        return None
