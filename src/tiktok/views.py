from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from automationapp import settings
from src.core.utils import full_url_for_route
from src.tiktok.models import TikTokUser
from src.tiktok.services.oauth.tiktok_oauth_service import TikTokOAuthService


@require_GET
def auth_redirect_to_tiktok(request: HttpRequest):
    """
    https://developers.tiktok.com/doc/login-kit-manage-user-access-tokens?enter_method=left_navigation
    """
    redirect_uri = _redirect_url(request.GET.get('tiktok_username'))
    url = f'https://www.tiktok.com/v2/auth/authorize/?client_key={settings.TIKTOK_CLIENT_KEY}&response_type=code&scope=user.info.basic&redirect_uri={redirect_uri}'

    return redirect(url)


@csrf_exempt
@login_required
def auth_redirect_from_tiktok(request: HttpRequest):
    user = request.user
    authorization_code = request.GET.get('code')
    tiktok_username = request.GET.get('tiktok_username')
    service = TikTokOAuthService()
    service.save_oauth_data(user, authorization_code, tiktok_username)
    return JsonResponse({})


def tiktok_accounts(request):
    tiktok_users = TikTokUser.objects.filter(user=request.user)
    return render(request, "tiktok_accounts.html", {
        "tiktok_users": tiktok_users
    })


def _redirect_url(tiktok_username: str):
    return full_url_for_route(
        'tiktok.auth_redirect_from_tiktok',
        query_params={'tiktok_username': tiktok_username}
    )
