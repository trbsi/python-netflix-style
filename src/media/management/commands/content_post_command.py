from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from django.db.models import QuerySet

from src.core.management.commands.base_command import BaseCommand
from src.media.models import PostContent
from src.tiktok.services.post.tiktok_poster_service import TikTokPostService


class ContentPostCommand(BaseCommand):
    POST_START = time(17, 0)
    POST_END = time(21, 0)

    def handle(self, *args, **options):
        tiktok = TikTokPostService()
        content: QuerySet[PostContent] = (
            PostContent.objects
            .exclude(status=PostContent.STATUS_UPLOADED)
            .exclude(site='all')
        )
        now_utc = datetime.now(timezone.utc)

        for single_content in content:
            local_time = now_utc.astimezone(ZoneInfo(single_content.timezone))
            if not (self.POST_START <= local_time.time() <= self.POST_END):
                continue

            day = local_time.day
            if (day % 2 == 0 and local_time.hour >= 19) or (day % 2 != 0 and local_time.hour <= 19):
                continue

            if single_content.is_tiktok():
                tiktok.post_content(single_content)
            elif single_content.is_facebook():
                pass
            else:
                continue

            single_content.status = PostContent.STATUS_UPLOADED
            single_content.save()

            if single_content.group:
                posts = PostContent.objects.filter(group=single_content.group).order_by('id')
                for post in posts:
                    post.status = PostContent.STATUS_UPLOADED
                    post.save()
