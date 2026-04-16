from django.urls import path

from . import views

urlpatterns = [
    path('categories/search', views.categories_search_api, name='media.api.categories_search'),
    path('search', views.search_videos_api, name='media.api.search'),
]
