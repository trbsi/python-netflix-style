from django.http import HttpRequest, JsonResponse

from src.discovery.services.personalization.personalize_site_service import PersonalizeSiteService


def discover_videos_api(request: HttpRequest) -> JsonResponse:
    text = request.GET.get('text')

    service = PersonalizeSiteService()
    tags = service.personalize_site(text)

    response = JsonResponse({})
    response.set_cookie(key='personalized_tags', value=tags, expires=None)

    return response
