from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.media.services.home.list_media_service import ListMediaService


def media_home(request: HttpRequest) -> HttpResponse:
    service = ListMediaService()
    videos = service.video_list()
    return render(request, 'home.html', videos)
