from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from src.media.models import VideoItem, VideoCategory
from src.media.services.categories.search_by_category_service import SearchByCategoryService
from src.media.services.home.list_media_service import ListMediaService


@require_GET
def media_home(request: HttpRequest) -> HttpResponse:
    service = ListMediaService()
    videos = service.home_video_list()
    return render(request, 'home/home.html', videos)


@require_GET
def single_video(request: HttpRequest, id: int) -> HttpResponse:
    video = VideoItem.objects.get(id=id)
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
    return render(request, 'categories/search.html', {'slug': slug})


@require_GET
def categories_search_api(request: HttpRequest) -> HttpResponse:
    get = request.GET
    service = SearchByCategoryService()
    videos, has_next = service.search_videos(get.get('slug'), int(get.get('page')))

    return JsonResponse({
        "videos": videos,
        "has_next": has_next
    })
