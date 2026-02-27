from celery import shared_task
from django.core.management import call_command


@shared_task
def import_from_rss_task():
    call_command('import_rss_feed_command')


@shared_task
def import_from_dump_task():
    call_command('import_dump_command')
