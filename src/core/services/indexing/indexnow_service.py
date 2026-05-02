import bugsnag
import requests
from django.core.cache import cache

from automationapp import settings
from src.core.utils import full_url_for_route
from src.media.models import VideoItem


class IndexNowService:
    CACHE_KEY = 'indexnow_last_video_id'
    BATCH = 300

    def send_urls_to_indexnow(self, is_dry_run=False):
        last_id = int(cache.get(self.CACHE_KEY, 0))
        videos: list[VideoItem] = list(VideoItem.objects.order_by('id')
                                       .filter(slug_rewritten__isnull=False)
                                       .filter(id__gt=last_id)[:self.BATCH])

        if not videos:
            print(f"No videos found for last_id: {last_id}")
            return

        urls = [
            video.video_full_url for video in videos
        ]

        host = (settings.APP_URL).replace('https://', '').replace('http://', '').replace('www.', '')
        body = {
            "host": host,
            "key": settings.INDEXNOW_API_KEY,
            "keyLocation": full_url_for_route('indexnow_key'),
            "urlList": urls
        }

        if is_dry_run:
            print(body)
            return

        result = requests.post(
            url='https://api.indexnow.org/indexnow',
            json=body
        )

        if result.status_code == 200:
            print(body)
            last_id = videos[-1].id
            cache.set(self.CACHE_KEY, last_id, timeout=None)
            bugsnag.notify(Exception(f"URLs submitted. Last id is {last_id}"))
        else:
            print(result.status_code)
            print(result.headers.get("Content-Type"))
            print(result.text)
            bugsnag.notify(Exception(f"IndexNow Error: {result.text}"))
