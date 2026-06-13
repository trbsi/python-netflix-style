import datetime
import json

from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from src.core.utils.utils import get_or_create_session
from src.discovery.services.personalization.llm_personalize_site_service import LlmPersonalizeSiteService
from src.discovery.services.personalization.personalize_site_service import PersonalizeSiteService
from src.discovery.services.search_tags.search_tags_service import SearchTagsService


@require_POST
def discover_videos_api(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body)
    text = body.get('text')
    selected_tag_ids = body.get('selected_tag_ids')
    get_or_create_session(request)

    if selected_tag_ids:
        service = PersonalizeSiteService()
        cookie_value = service.personalize_site(text, selected_tag_ids, request.session.session_key)
    else:
        service = LlmPersonalizeSiteService()
        cookie_value = service.personalize_site(text, request.session.session_key)

    response = JsonResponse({})
    if cookie_value:
        expires = timezone.now() + datetime.timedelta(days=90)
        response.set_cookie(key='personalized_tags', value=cookie_value, expires=expires)

    return response


@require_POST
def search_tags_api(request: HttpRequest) -> JsonResponse:
    body = json.loads(request.body)
    service = SearchTagsService()
    tags = service.search_tags(body.get('tag'), body.get('tag_groups'))

    return JsonResponse({'tags': tags})
