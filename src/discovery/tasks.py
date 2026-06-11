from celery import shared_task
from django.core.management import call_command


@shared_task
def canonical_tags_task():
    call_command(
        'canonical_tags_command',
        steps=['extract_raw', 'insert_clean_tags'],
    )
