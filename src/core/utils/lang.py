from django.utils import translation

from automationapp import settings


def get_active_language():
    lang = translation.get_language()
    return lang.split('-')[0]


def get_language_codes():
    return [
        code for code, lang in settings.SUPPORTED_LANGUAGES
    ]
