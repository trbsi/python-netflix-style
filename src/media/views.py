import pytz
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST, require_GET

from src.media.models import PostContent
from src.media.services.update.update_media_service import UpdateMediaService
from src.media.services.upload.upload_file_service import UploadFileService


@require_POST
@login_required
def upload_file(request):
    context = {
        "timezones": pytz.all_timezones,
        "form_data": {}
    }

    if request.method == "POST":
        form_data = request.POST.dict()
        context["form_data"] = form_data
        file = request.FILES.get("file")

        service = UploadFileService()
        service.upload_file(request.user, file, form_data)

        return redirect(reverse_lazy('media.list'))

    return render(request, "post_content_form.html", context)


@require_GET
@login_required
def list_files(request):
    posts = PostContent.objects.filter(user=request.user)
    return render(request, "post_content_list.html", {"posts": posts})


@require_POST
@login_required
def edit_post_content(request, post_id):
    service = UpdateMediaService()
    service.update_media()
    return redirect(reverse_lazy('media.list'))
