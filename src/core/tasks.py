from celery import shared_task
from django.core.management import call_command


@shared_task
def indexnow_task():
    call_command('indexnow_command')


@shared_task
def geoip_database_task():
    call_command('geoip_command')
