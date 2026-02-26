from celery import shared_task
from django.core.management import call_command


@shared_task
def import_from_rss():
    call_command('import_rss_feed_command')
