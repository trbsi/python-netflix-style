from celery import shared_task
from django.core.management import call_command


@shared_task
def reply_to_conversations_task():
    call_command('reply_to_conversations_command')
