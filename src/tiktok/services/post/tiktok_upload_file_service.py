import mimetypes
import os

import requests

from src.core.utils import get_access_token


class TikTokUploadFileService:
    # https://developers.tiktok.com/doc/content-posting-api-get-started-upload-content?enter_method=left_navigation
    # https://developers.tiktok.com/doc/content-posting-api-reference-upload-video#
    def upload_video(self, file_path: str, tiktok_username: str):
        data = self._get_upload_url(tiktok_username, file_path)
        self._upload_to_tiktok(data, file_path)

    def _upload_to_tiktok(self, data: dict, file_path: str):
        mime_type, encoding = mimetypes.guess_type(file_path)
        headers = {
            "Content-Type": mime_type,
        }

        with open(file_path, "rb") as f:
            response = requests.put(data['upload_url'], headers=headers, data=f)

        print(response.text)

    def _get_upload_url(self, tiktok_username: str, file_path: str):
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
        url = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
        size_bytes = os.path.getsize(file_path)

        headers = {
            "Authorization": "Bearer " + get_access_token(tiktok_username),
            "Content-Type": "application/json",
        }

        payload = {
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size_bytes,
                "chunk_size": size_bytes,
                "total_chunk_count": 1
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        return result['data']
