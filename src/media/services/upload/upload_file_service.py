from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile

from src.media.models import PostContent
from src.user.models import User


class UploadFileService():
    def upload_file(self, user: User, file: UploadedFile, data: dict):
        fs = FileSystemStorage()
        file_name = fs.save(file.name, file)

        PostContent.objects.create(
            user=user,
            content_type=data.get("content_type"),
            site=data.get("site"),
            site_username=data.get("site_username"),
            title=data.get("title"),
            content=data.get("content"),
            file_name=file_name,
            status=data.get("status"),
        )
