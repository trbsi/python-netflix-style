from django.urls import path

from . import views

urlpatterns = [
    path('<int:id>', views.single_video, name='media.single_video'),
    path('play/<int:id>', views.play_video, name='media.play_video'),
]
