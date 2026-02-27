from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.media.models import VideoItem
from src.media.services.home.list_media_service import ListMediaService


def media_home(request: HttpRequest) -> HttpResponse:
    service = ListMediaService()
    videos = service.home_video_list()
    print((videos['top_10_movies']))
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
