from django.urls import path

from . import views

urlpatterns = [
    path('categories', views.categories, name='media.categories'),
    path('categories/<str:slug>', views.categories_search, name='media.categories_search'),
    path('play/<int:id>', views.play_video, name='media.play_video'),
    path('search', views.search_videos, name='media.search'),
    path('all', views.all_videos, name='media.all_videos'),
    path('<int:id>/<str:slug>', views.single_video, name='media.single_video'),
]
