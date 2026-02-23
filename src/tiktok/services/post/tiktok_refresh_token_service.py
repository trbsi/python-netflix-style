import requests

from automationapp import settings
from src.core.utils import save_to_cache, get_refresh_token


class TikTokRefreshTokenService:
    def refresh_token(self, tiktok_username: str):
        """
        https://developers.tiktok.com/doc/oauth-user-access-token-management?enter_method=left_navigation
        {
            "access_token": "act.example12345Example12345Example",
            "expires_in": 86400,
            "open_id": "asdf-12345c-1a2s3d-ac98-asdf123as12as34",
            "refresh_expires_in": 31536000,
            "refresh_token": "rft.example12345Example12345Example",
            "scope": "user.info.basic,video.list",
            "token_type": "Bearer"
        }
        """
        payload = {
            "client_key": settings.TIKTOK_CLIENT_KEY,
            "client_secret": settings.TIKTOK_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": get_refresh_token(tiktok_username),
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        }

        response = requests.post(
            'https://open.tiktokapis.com/v2/oauth/token/', data=payload, headers=headers
        )
        result = response.json()

        save_to_cache(result, tiktok_username)
