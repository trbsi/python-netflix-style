import pytz
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST, require_GET

from src.media.models import PostContent, SocialAccount
from src.media.services.update.update_media_service import UpdateMediaService
from src.media.services.upload.upload_file_service import UploadFileService


@login_required
def upload_file(request):
    context = {
        'timezones': [
            pytz.timezone("America/New_York"),
            pytz.timezone("Europe/Zagreb")
        ],  # pytz.all_timezones,
        'form_data': {},
        'social_accounts': SocialAccount.objects.order_by('site').all(),
        'sites': PostContent.SITES
    }

    if request.method == 'POST':
        form_data = request.POST.dict()
        context['form_data'] = form_data
        file = request.FILES.get('file')

        service = UploadFileService()
        service.upload_file(request.user, file, form_data)

        return redirect(reverse_lazy('media.list'))

    return render(request, 'post_content_form.html', context)


@require_GET
@login_required
def list_files(request):
    posts = PostContent.objects.filter(user=request.user)
    context = {
        'timezones': [
            pytz.timezone("America/New_York"),
            pytz.timezone("Europe/Zagreb")
        ],  # pytz.all_timezones,
        'form_data': {},
        'social_accounts': SocialAccount.objects.order_by('site').all(),
        'posts': posts,
        'sites': PostContent.SITES
    }
    return render(request, 'post_content_list.html', context)


@require_POST
@login_required
def edit_post_content(request: HttpRequest):
    service = UpdateMediaService()
    service.update_media(
        int(request.POST.get('post_id')),
        request.user,
        request.POST,
        request.FILES.get("file")
    )
    return redirect(reverse_lazy('media.list'))
