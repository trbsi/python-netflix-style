from celery import shared_task
from django.core.management import call_command


@shared_task
def indexnow_task():
    call_command('indexnow_command')
