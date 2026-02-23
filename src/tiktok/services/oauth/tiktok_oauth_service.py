import requests

from automationapp import settings
from src.core.utils import save_to_cache
from src.tiktok.models import TikTokUser
from src.tiktok.views import _redirect_url
from src.user.models import User


class TikTokOAuthService:
    def save_oauth_data(self, user: User, authorization_code: str, tiktok_username: str):
        """
        https://developers.tiktok.com/doc/oauth-user-access-token-management?enter_method=left_navigation
        {
            "access_token": "act.example12345Example12345Example",
            "expires_in": 86400,
            "open_id": "afd97af1-b87b-48b9-ac98-410aghda5344",
            "refresh_expires_in": 31536000,
            "refresh_token": "rft.example12345Example12345Example",
            "scope": "user.info.basic,video.list",
            "token_type": "Bearer"
        }
        """

        payload = {
            "client_key": settings.TIKTOK_CLIENT_KEY,
            "client_secret": settings.TIKTOK_CLIENT_SECRET,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": _redirect_url(tiktok_username),
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
        }

        response = requests.post(
            'https://open.tiktokapis.com/v2/oauth/token/', data=payload, headers=headers
        )
        result = response.json()

        tiktok_model = TikTokUser()
        tiktok_model.user = user
        tiktok_model.tiktok_username = tiktok_username
        tiktok_model.save()

        save_to_cache(result, tiktok_username)
