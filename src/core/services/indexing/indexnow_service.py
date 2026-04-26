import bugsnag
import requests
from django.core.cache import cache
from django.db.models import QuerySet

from automationapp import settings
from src.core.utils import full_url_for_route
from src.media.models import VideoItem


class IndexNowService:
    CACHE_KEY = 'indexnow_last_video_id'
    BATCH = 300

    def send_urls_to_indexnow(self, is_dry_run=False):
        last_id = int(cache.get(self.CACHE_KEY, 0))
        videos: QuerySet[VideoItem] = VideoItem.objects.order_by('-id').filter(id__gt=last_id)[:self.BATCH]

        if not videos:
            return

        urls = [
            video.video_full_url for video in videos
        ]

        host = (settings.APP_URL).replace('https://', '').replace('http://', '').replace('www.', '')
        body = {
            "host": f"www.{host}",
            "key": settings.INDEXNOW_API_KEY,
            "keyLocation": full_url_for_route('indexnow_key'),
            "urlList": urls
        }

        if is_dry_run:
            print(body)
            return

        result = requests.post(
            url='https://www.indexnow.com/api/v2/videos/',
            json=body
        )

        if result.status_code == 200:
            print(body)
            last_id = videos[-1].id
            cache.set(self.CACHE_KEY, last_id, timeout=None)
            bugsnag.notify(Exception(f"URLs submitted. Last id is {last_id}"))
        else:
            bugsnag.notify(Exception(f"IndexNow Error: {result.json()}"))
