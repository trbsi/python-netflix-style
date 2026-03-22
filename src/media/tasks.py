import os
import shutil

from celery import shared_task
from django.core.management import call_command

from src.media.services.import_dump.download_zip_service import DownloadZipService


@shared_task
def import_from_rss_task():
    call_command('import_rss_feed_command')


@shared_task
def import_from_dump_partial_task(site):
    call_command('import_dump_command', site)


@shared_task
def delete_videos_task(site):
    call_command('delete_videos_command', site)


@shared_task
def generate_frontpage_task():
    call_command('generate_frontpage_command')


@shared_task
def clean_extract_directory_task():
    if os.path.exists(DownloadZipService.EXTRACT_DIR):
        shutil.rmtree(DownloadZipService.EXTRACT_DIR)
