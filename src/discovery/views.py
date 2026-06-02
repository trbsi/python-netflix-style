import datetime
import json

from django.http import HttpRequest, JsonResponse
from django.utils import timezone

from src.core.utils.utils import get_or_create_session
from src.discovery.services.personalization.llm_personalize_site_service import LlmPersonalizeSiteService


def discover_videos_api(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body)
    text = body.get('text')
    get_or_create_session(request)

    service = LlmPersonalizeSiteService()
    cookie_value = service.personalize_site(text, request.session.session_key)

    response = JsonResponse({})
    if cookie_value:
        expires = timezone.now() + datetime.timedelta(days=90)
        response.set_cookie(key='personalized_tags', value=cookie_value, expires=expires)

    return response
