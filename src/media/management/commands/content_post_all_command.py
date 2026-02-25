from datetime import time

from django.db.models import QuerySet

from src.core.management.commands.base_command import BaseCommand
from src.media.models import PostContent
from src.tiktok.services.post.tiktok_poster_service import TikTokPostService


class ContentPostAllCommand(BaseCommand):
    POST_START = time(17, 0)
    POST_END = time(21, 0)

    def handle(self, *args, **options):
        tiktok = TikTokPostService()
        content: QuerySet[PostContent] = (
            PostContent.objects
            .exclude(status=PostContent.STATUS_UPLOADED)
            .filter(site='all')
        )

        for single_content in content:
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