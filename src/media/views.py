from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.media.models import VideoItem, VideoCategory
from src.media.services.categories.search_by_category_service import SearchByCategoryService
from src.media.services.home.list_media_service import ListMediaService


def media_home(request: HttpRequest) -> HttpResponse:
    service = ListMediaService()
    videos = service.home_video_list()
    return render(request, 'home/home.html', videos)


def single_video(request: HttpRequest, id: int) -> HttpResponse:
    video = VideoItem.objects.get(id=id)
    service = ListMediaService()
    videos = service.single_video_list()
    context = {'video': video} | videos
    return render(request, 'single_video/video_detail.html', context)


def play_video(request: HttpRequest, id: int) -> HttpResponse:
    video = VideoItem.objects.get(id=id)
    context = {'video': video}
    return render(request, 'single_video/video_player.html', context)


def categories(request: HttpRequest) -> HttpResponse:
    context = {'categories': VideoCategory.objects.all()}
    return render(request, 'categories/categories.html', context)


def categories_search(request: HttpRequest, slug: str) -> HttpResponse:
    service = SearchByCategoryService()
    context = {'videos': service.search_videos(slug)}
    return render(request, 'categories/search.html', context)
