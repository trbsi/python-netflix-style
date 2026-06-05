from django.urls import path

from . import views

urlpatterns = [
    path('api/discover-videos', views.discover_videos_api, name='media.api.discover_videos'),
    path('api/search-tags', views.search_tags_api, name='media.api.search_tags'),
]
