import json

from django.http import HttpRequest, JsonResponse

from src.core.utils.utils import get_or_create_session
from src.discovery.services.personalization.personalize_site_service import PersonalizeSiteService


def discover_videos_api(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body)
    text = body.get('text')
    get_or_create_session(request)

    service = PersonalizeSiteService()
    tags = service.personalize_site(text, request.session.session_key)

    response = JsonResponse({})
    if tags:
        response.set_cookie(key='personalized_tags', value=tags, expires=None)

    return response
