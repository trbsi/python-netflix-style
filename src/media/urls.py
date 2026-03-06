from django.urls import path

from . import views

urlpatterns = [
    path('categories', views.categories, name='media.categories'),
    path('categories/<str:slug>', views.categories_search, name='media.categories_search'),
    path('api/categories/search', views.categories_search_api, name='media.api.categories_search'),
    path('<int:id>', views.single_video, name='media.single_video'),
    path('play/<int:id>', views.play_video, name='media.play_video'),
]
