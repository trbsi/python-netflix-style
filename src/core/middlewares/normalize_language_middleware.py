from django.utils import translation


class NormalizeLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = translation.get_language_from_request(request)

        if lang and '-' in lang:
            lang = lang.split('-')[0]  # en-gb → en

        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        return self.get_response(request)
