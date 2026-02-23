from celery import shared_task
from django.core.management import call_command


@shared_task
def post_content_task():
    call_command("content_post_command")
