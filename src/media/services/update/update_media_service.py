import os

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import get_object_or_404

from src.media.models import PostContent
from src.user.models import User


class UpdateMediaService():
    def update_media(
            self,
            post_id: int,
            user: User,
            data: dict,
            file: None | UploadedFile
    ):
        post = get_object_or_404(PostContent, id=post_id, user=user)
        if data.get("delete_file"):
            if post.file_name:
                path = post.get_file_path()
                if os.path.exists(path):
                    os.remove(path)
            post.delete()
        else:
            post.content_type = data.get("content_type")
            post.site = data.get("site")
            post.site_username = data.get("site_username")
            post.title = data.get("title")
            post.content = data.get("content")
            post.timezone = data.get("timezone")
            post.status = data.get("status")

            if file:
                fs = FileSystemStorage()
                post.file_name = fs.save(file.name, file)

            post.save()
