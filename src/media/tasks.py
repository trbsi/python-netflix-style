import os
import shutil

from celery import shared_task
from django.core.management import call_command

from automationapp import settings
from src.media.services.import_dump.download_zip_service import DownloadZipService


# ------------ CLEAN EXTRACT DIRECTORY --------------
@shared_task
def clean_extract_directory_task():
    if os.path.exists(DownloadZipService.EXTRACT_DIR):
        shutil.rmtree(DownloadZipService.EXTRACT_DIR)


# ------------ DUMP IMPORT ----------------------
@shared_task
def import_from_dump_partial_for_enabled_sites_task():
    for site in settings.ENABLED_SITES:
        call_command('import_dump_command', site)


# ------------ DUMP IMPORT ----------------------

@shared_task
def delete_videos_for_enabled_sites_task():
    for site in settings.ENABLED_SITES:
        call_command('delete_videos_command', site)


# ------------ FRONTPAGE  ----------------------
@shared_task
def generate_frontpage_task():
    call_command('generate_frontpage_command')


# ------------ AI Rewrite  ----------------------
@shared_task
def rewrite_title_send_to_batch_task(batch_size):
    call_command('rewrite_title_command', 'send_to_batch', batch_size)


@shared_task
def rewrite_title_check_batch_task():
    call_command('rewrite_title_command', 'check_batch')
