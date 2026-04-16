import json

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from automationapp import settings
from src.core.utils import unslugify
from src.media.models import VideoItem, VideoCategory
from src.media.services.all_videos.all_videos_service import AllVideosService
from src.media.services.categories.search_by_category_service import SearchByCategoryService
from src.media.services.frontpage.list_media_service import ListMediaService
from src.media.services.search.search_fulltext_service import SearchFullTextService
from src.media.services.title_rewrite.local_rewrite import LocalRewriteService


@require_GET
def media_home(request: HttpRequest) -> HttpResponse:
    if settings.APP_ENV != 'production':
        service = ListMediaService()
        videos = service.home_video_list()
        return render(request, 'home/home.html', videos)

    html = cache.get('frontpage_html')

    if not html:
        service = ListMediaService()
        videos = service.home_video_list()
        html = render(request, 'home/home.html', videos).content
        cache.set('frontpage_html', html, 60 * 60)

    return HttpResponse(html)


@require_GET
def single_video(request: HttpRequest, id: int, slug: str) -> HttpResponse:
    video = get_object_or_404(VideoItem, pk=id)
    service = ListMediaService()
    videos = service.single_video_list()
    context = {'video': video} | videos
    return render(request, 'single_video/video_detail.html', context)


@require_GET
def play_video(request: HttpRequest, id: int) -> HttpResponse:
    video = VideoItem.objects.get(id=id)
    context = {'video': video}
    return render(request, 'single_video/video_player.html', context)


@require_GET
def categories(request: HttpRequest) -> HttpResponse:
    context = {'categories': VideoCategory.objects.all()}
    return render(request, 'categories/categories.html', context)


@require_GET
def categories_search(request: HttpRequest, slug: str) -> HttpResponse:
    category = unslugify(slug)
    service = SearchByCategoryService()
    page_obj = service.search_videos(slug, int(request.GET.get('page', 1)))

    context = {'category': category, 'slug': slug, 'page_obj': page_obj}
    return render(request, 'categories/search.html', context)


@require_GET
def categories_search_api(request: HttpRequest) -> HttpResponse:
    get = request.GET
    last_id = int(get.get('last_id')) if get.get('last_id') else 0
    query = get.get('query')

    service = SearchByCategoryService()
    videos, has_next = service.search_videos_api(query, last_id)

    return JsonResponse({
        "videos": videos,
        "has_next": has_next
    })


@require_GET
def search_videos(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('query')
    return render(request, 'search/search.html', {'query': query})


@require_GET
def all_videos(request: HttpRequest) -> HttpResponse:
    page = int(request.GET.get('page', 1))
    service = AllVideosService()
    page_obj = service.get_all_videos(page)

    return render(
        request,
        'videos/all_videos.html',
        {'page_obj': page_obj}
    )


@require_GET
def search_videos_api(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('query')
    scroll_cursor = request.GET.get('scroll_cursor')

    service = SearchFullTextService()
    result = service.search_media(query, scroll_cursor)

    return JsonResponse({
        "videos": result.to_array(),
        "scroll_cursor": result.scroll_cursor,
        "has_next": True
    })


@require_POST
@csrf_exempt
def update_title_rewritten_api(request: HttpRequest) -> JsonResponse:
    payload = json.loads(request.body)
    service = LocalRewriteService()
    updated = service.update_titles(payload)

    return JsonResponse({"updated": updated})


@require_GET
def get_title_rewritten_api(request: HttpRequest) -> JsonResponse:
    get = request.GET
    limit = int(get.get("limit", 10))
    count = bool(get.get("count")) if get.get("count") else False
    latest = bool(get.get("latest")) if get.get("latest") else False

    service = LocalRewriteService()
    result = service.get_videos_for_rewrite(limit, count, latest)

    return JsonResponse(result)
