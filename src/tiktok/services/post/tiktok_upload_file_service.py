import mimetypes
import os

import requests

from automationapp import settings
from src.core.utils import get_access_token
from src.media.models import PostContent


class TikTokUploadFileService:
    # https://developers.tiktok.com/doc/content-posting-api-get-started-upload-content?enter_method=left_navigation
    # https://developers.tiktok.com/doc/content-posting-api-reference-upload-video#
    def upload_video(self, content: PostContent):
        if content.is_video():
            data = self._get_upload_url(content)
            self._upload_video(data, content)
        else:
            self._upload_image(content)

    def _upload_image(self, content: PostContent):
        url = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"

        headers = {
            "Authorization": "Bearer " + get_access_token(content.site_username),
            "Content-Type": "application/json",
        }

        payload = {
            "post_info": {
                "title": content.title,
                "description": content.content
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "photo_cover_index": 1,
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "photo_images": self._get_files(content),
            },
            "post_mode": "DIRECT_POST",
            "media_type": "PHOTO"
        }

        proxies = {}
        if content.needs_proxy():
            proxies = {
                "http": settings.HTTP_PROXY,
                "https": settings.HTTP_PROXY,
            }

        response = requests.post(url, headers=headers, json=payload, proxies=proxies)
        print(response.json())

    def _get_files(self, content:PostContent)->list:
        if not content.group:
            return [content.get_file_url()]

        result = []
        posts = PostContent.objects.filter(group=content.group).order_by('id')
        for post in posts:
            result.append(post.get_file_url())

        return result

    def _upload_video(self, data: dict, content: PostContent):
        file_path = content.get_file_path()
        mime_type, encoding = mimetypes.guess_type(file_path)
        headers = {
            "Content-Type": mime_type,
        }

        proxies = {}
        if content.needs_proxy():
            proxies = {
                "http": settings.HTTP_PROXY,
                "https": settings.HTTP_PROXY,
            }

        with open(file_path, "rb") as file:
            response = requests.put(data['upload_url'], headers=headers, data=file, proxies=proxies)

        print(response.json())

    def _get_upload_url(self, content: PostContent):
        """
        {
            "data": {
                "publish_id": "v_inbox_file~v2.123456789",
                "upload_url": "https://open-upload.tiktokapis.com/video/?upload_id=67890&upload_token=Xza123"
            },
            "error": {
                 "code": "ok",
                 "message": "",
                 "log_id": "202210112248442CB9319E1FB30C1073F3"
             }
        }
        """
        tiktok_username = content.site_username
        file_path = content.get_file_path()
        url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        size_bytes = os.path.getsize(file_path)

        headers = {
            "Authorization": "Bearer " + get_access_token(tiktok_username),
            "Content-Type": "application/json",
        }

        payload = {
            "post_info": {
                "title": content.content,
                "privacy_level": "PUBLIC_TO_EVERYONE",
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size_bytes,
                "chunk_size": size_bytes,
                "total_chunk_count": 1
            }
        }

        proxies = {}
        if content.needs_proxy():
            proxies = {
                "http": settings.HTTP_PROXY,
                "https": settings.HTTP_PROXY,
            }

        response = requests.post(url, headers=headers, json=payload, proxies=proxies)
        result = response.json()

        return result['data']
