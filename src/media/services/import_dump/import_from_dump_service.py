import os
import shutil

from django.utils import timezone

from src.media.models import VideoItem
from src.media.services.import_dump.download_zip_service import DownloadZipService
from src.media.services.import_dump.dump_to_database_service import DumpToDatabaseService
from src.media.services.manticore.manticore_service import ManticoreService


class ImportFromDumpService:
    def __init__(self):
        self.search_index_service = ManticoreService()
        self.dump_to_database_service = DumpToDatabaseService()
        self.download_zip_service = DownloadZipService()

    def import_from_dump(self, site: str, import_all: bool = False) -> list:
        self._init(site)

        csv_file_path = self.download_zip_service.download_zip(
            self.ZIP_URL,
            self.ZIP_FILE,
            import_all
        )

        self.search_index_service.create_index()
        total_imported = self.dump_to_database_service.save_to_database(
            site,
            self.fields_map,
            csv_file_path
        )

        shutil.rmtree(DownloadZipService.EXTRACT_DIR)
        os.remove(self.ZIP_FILE)

        today = timezone.now().date()
        count_today = VideoItem.objects.filter(external_created_at=today).count()

        return [total_imported, count_today]

    def _init(self, site: str):
        if site == 'pornhub':
            self.ZIP_URL = "https://www.pornhub.com/files/pornhub.com-db.zip"
            self.ZIP_FILE = "pornhub.com-db.zippornhub_db.zip"
            self.fields_map = {
                'fields_split_by': '|',
                'categories_split_by': ';',
                'categories': 5,
                'title': 3,
                'duration': 7,
                'thumb_small': 2,
                'thumb_large': 12,
                'embed_code': 0,
                'tags': 4,
                'external_id': 0,
                'external_created_at': 2,
                'url': 999,
            }
        elif site == 'eporner':
            self.ZIP_URL = 'https://www.eporner.com/sitemap/feeds/eporner_hq_640x360.txt.zip'
            self.ZIP_FILE = 'eporner_hq_640x360.txt.zip'
            self.fields_map = {
                'fields_split_by': '|',
                'categories_split_by': ',',
                'categories': 4,
                'title': 3,
                'duration': 2,
                'thumb_small': 6,
                'thumb_large': 6,
                'embed_code': 999,
                'tags': 5,
                'external_id': 0,
                'external_created_at': 999,
                'url': 1,
            }
        elif site == 'xvideos':
            self.ZIP_URL = 'https://public-assets.xvideos-cdn.com/webmaster-tools/xvideos.com-export-week.csv.zip'
            self.ZIP_FILE = 'xvideos.com-export.csv.zip'
            self.fields_map = {
                'fields_split_by': ';',
                'categories_split_by': ',',
                'categories': 8,
                'title': 1,
                'duration': 2,
                'thumb_small': 3,
                'thumb_large': 3,
                'embed_code': 4,
                'tags': 5,
                'external_id': 7,
                'external_created_at': 12,
                'url': 0,
            }
