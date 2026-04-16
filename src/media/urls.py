from django.urls import path

from . import views

urlpatterns = [
    path('api/categories/search', views.categories_search_api, name='media.api.categories_search'),
    path('api/search', views.search_videos_api, name='media.api.search'),
    path('api/update-title', views.update_title_rewritten_api),
    path('api/get-title', views.get_title_rewritten_api),

    path('<str:lang>/categories', views.categories, name='media.categories'),
    path('<str:lang>/categories/<str:slug>', views.categories_search, name='media.categories_search'),
    path('<str:lang>/play/<int:id>', views.play_video, name='media.play_video'),
    path('<str:lang>/search', views.search_videos, name='media.search'),
    path('<str:lang>/all', views.all_videos, name='media.all_videos'),

    path('<str:lang>/<int:id>/<str:slug>', views.single_video, name='media.single_video'),
]
