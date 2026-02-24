from django.urls import path

from . import views

urlpatterns = [
    path("upload", views.upload_file, name="media.upload"),
    path("list", views.list_files, name="media.list"),
    path("edit", views.edit_post_content, name="media.edit"),
]
