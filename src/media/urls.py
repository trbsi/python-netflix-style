from django.urls import path

from . import views

urlpatterns = [
    path('categories', views.categories, name='media.categories'),
    path('categories/<str:slug>', views.categories_search, name='media.categories_search'),
    path('play/<int:id>', views.play_video, name='media.play_video'),
    path('search', views.search_videos, name='media.search'),
    
    path('api/categories/search', views.categories_search_api, name='media.api.categories_search'),
    path('api/search', views.search_videos_api, name='media.api.search'),
    path('api/update-title', views.update_title_rewritten_api),
    path('api/get-title', views.get_title_rewritten_api),

    path('<int:id>/<str:slug>', views.single_video, name='media.single_video'),
]
