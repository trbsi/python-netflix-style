from celery import chain
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.media.tasks import generate_frontpage_task, \
    import_from_dump_partial_for_enabled_sites_task, delete_videos_for_enabled_sites_task
from src.sitemap.tasks import generate_sitemap_partial_task


@staff_member_required
def commands(request: HttpRequest) -> HttpResponse:
    site = request.GET.get('site')
    batch_size = request.GET.get('batch_size')
    return render(
        request,
        "admin_commands.html",
        {'site': site, 'batch_size': batch_size}
    )


@staff_member_required
def trigger_partial_import(request: HttpRequest) -> HttpResponse:
    chain(
        import_from_dump_partial_for_enabled_sites_task.si(),
        delete_videos_for_enabled_sites_task.si()
    ).delay()

    return HttpResponse(
        'import_from_dump_partial_for_enabled_sites_task, delete_videos_for_enabled_sites_task are queued', status=200)


@staff_member_required
def trigger_generate_frontend(request: HttpRequest) -> HttpResponse:
    generate_frontpage_task.delay()
    return HttpResponse('generate_frontpage_task is queued', status=200)


@staff_member_required
def trigger_sitemap_partial(request: HttpRequest) -> HttpResponse:
    generate_sitemap_partial_task.delay()
    return HttpResponse('generate_sitemap_partial_task is queued', status=200)
