from celery import chain
from django.http import HttpRequest, HttpResponse

from src.media.tasks import import_from_dump_partial_task, delete_videos_task, generate_frontpage_task


def trigger_import(request: HttpRequest) -> HttpResponse:
    site = request.GET.get('site')
    if not site:
        return HttpResponse('site is required', status=400)

    chain(
        import_from_dump_partial_task.si(site),
        delete_videos_task.si(site)
    ).delay()

    print(site)

    return HttpResponse('import_from_dump_partial_task, delete_videos_task are queued', status=200)


def trigger_generate_frontend(request: HttpRequest) -> HttpResponse:
    generate_frontpage_task.delay()
    return HttpResponse('generate_frontpage_task is queued', status=200)
