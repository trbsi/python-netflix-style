from src.core.utils import get_access_token
from src.media.models import PostContent
from src.tiktok.services.post.tiktok_refresh_token_service import TikTokRefreshTokenService
from src.tiktok.services.post.tiktok_upload_file_service import TikTokUploadFileService


class TikTokPostService:
    def __init__(self):
        self.upload_file_service = TikTokUploadFileService()
        self.refresh_token_service = TikTokRefreshTokenService()

    def post_content(self, content: PostContent):
        tiktok_username = content.site_username
        access_token = get_access_token(tiktok_username)
        if not access_token:
            self.refresh_token_service.refresh_token(tiktok_username)

        self.upload_file_service.upload_video(content)
        content.status = PostContent.STATUS_UPLOADED
        content.save()
