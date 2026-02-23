from django.db.models import QuerySet

from src.core.management.commands.base_command import BaseCommand
from src.post.models import PostContent
from src.tiktok.services.post.tiktok_poster_service import TikTokPostService


class ContentPostCommand(BaseCommand):
    def handle(self, *args, **options):
        tiktok = TikTokPostService()
        content: QuerySet[PostContent] = PostContent.objects.exclude(status=PostContent.STATUS_UPLOADED)
        for single_content in content:
            if single_content.is_tiktok():
                tiktok.post_content(single_content)
            elif single_content.is_facebook():
                pass
            elif single_content.is_linkedin():
                pass
