import os
import shutil

from src.media.models import VideoItem
from src.media.services.import_dump.download_zip_service import DownloadZipService


class DeleteVideosService:
    def __init__(self):
        self.download_zip_service = DownloadZipService()

    def remove_deleted_videos_from_database(self, site: str) -> int:
        self._init(site)
        total_deleted = 0

        csv_file_path = self.download_zip_service.download_zip(self.ZIP_URL, self.ZIP_FILE, True)

        with open(csv_file_path, 'r') as csv_file:
            for row in csv_file:
                row = row.split(self.fields_map['fields_split_by'])
                url = row[1]
                [num_deleted, num_deleted_per_model] = VideoItem.objects.filter(link=url).delete()
                total_deleted += num_deleted

        shutil.rmtree(DownloadZipService.EXTRACT_DIR)
        os.remove(self.ZIP_FILE)

        return total_deleted

    def _init(self, site: str):
        if site == 'xvideos':
            self.ZIP_URL = 'https://public-assets.xvideos-cdn.com/webmaster-tools/xvideos.com-deleted-week.csv.zip'
            self.ZIP_FILE = 'xvideos.com-deleted.csv.zip'
            self.fields_map = {
                'fields_split_by': '|'
            }
