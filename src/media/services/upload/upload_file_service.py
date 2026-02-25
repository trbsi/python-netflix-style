from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile

from src.media.models import PostContent
from src.user.models import User


class UploadFileService():
    def upload_file(self, user: User, file: UploadedFile, data: dict):
        fs = FileSystemStorage()
        path = f'{user.id}/{file.name}'
        file_name = fs.save(path, file)
        mime_type = file.content_type
        main_type = mime_type.split("/")[0]

        PostContent.objects.create(
            user=user,
            content_type=main_type,
            site=data.get("site"),
            site_username=data.get("social_account"),
            title=data.get("title"),
            content=data.get("content"),
            file_name=file_name,
            timezone=data.get("timezone"),
            status=PostContent.STATUS_NONE,
            group=data.get("group") or None,
        )
