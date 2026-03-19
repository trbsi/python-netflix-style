from celery import shared_task
from django.core.management import call_command


@shared_task
def generate_sitemap_full_task():
    call_command('generate_sitemap_command', full=True)


@shared_task
def generate_sitemap_partial_task():
    call_command('generate_sitemap_command', full=False)
