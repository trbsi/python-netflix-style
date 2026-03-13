import os
import shutil

from src.media.models import VideoItem
from src.media.services.import_dump.download_zip_service import DownloadZipService
from src.media.services.manticore.manticore_service import ManticoreService


class DeleteVideosService:
    def __init__(self):
        self.download_zip_service = DownloadZipService()
        self.search_index_service = ManticoreService()

    def remove_deleted_videos_from_database(self, site: str) -> int:
        self._init(site)

        total_deleted = 0
        csv_file_path = self.download_zip_service.download_zip(self.ZIP_URL, self.ZIP_FILE, True)

        print('Deleting videos...')
        with open(csv_file_path, 'r') as csv_file:
            for row in csv_file:
                row = row.split(self.fields_map['fields_split_by'])
                url = row[1].strip()

                videos = VideoItem.objects.filter(link=url)
                ids = list(videos.values_list('id', flat=True))
                self.search_index_service.delete_by_ids(ids)

                [num_deleted, num_deleted_per_model] = videos.delete()

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
