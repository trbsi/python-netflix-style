import os
import shutil
import zipfile
from collections import deque
from datetime import datetime

import requests

from automationapp import settings
from src.media.services.import_dump.dump_to_database_service import DumpToDatabaseService
from src.media.services.manticore.manticore_service import ManticoreService


class ImportFromDumpService:
    EXTRACT_DIR = "videos_dump_data"

    def __init__(self):
        self.search_index_service = ManticoreService()
        self.dump_to_database_service = DumpToDatabaseService()

    def import_from_dump(self, site: str, import_all: bool = False) -> int:
        self._init(site)

        # 1. Download zip file
        if self._should_download_zip():
            print("Downloading ZIP...")
            proxies = {}
            if settings.HTTP_PROXY:
                proxies = {
                    "http": settings.HTTP_PROXY,
                    "https": settings.HTTP_PROXY,
                }
            response = requests.get(self.ZIP_URL, stream=True, proxies=proxies)
            response.raise_for_status()

            with open(self.ZIP_FILE, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print("Download complete.")
        else:
            print('ZIP file exists for today')

        # 2. Extract zip locally
        print("Extracting ZIP...")
        os.makedirs(self.EXTRACT_DIR, exist_ok=True)

        with zipfile.ZipFile(self.ZIP_FILE, "r") as zip_ref:
            zip_ref.extractall(self.EXTRACT_DIR)

        print("Extraction complete.")

        # 3. Find CSV file
        csv_file_path = None
        for root, dirs, files in os.walk(self.EXTRACT_DIR):
            for file in files:
                if file.endswith(".csv") or file.endswith(".txt"):
                    csv_file_path = os.path.join(root, file)
                    break

        if not csv_file_path:
            raise Exception("CSV file not found after extraction.")

        # Create new file with last 100k rows
        if not import_all:
            with open(csv_file_path, "r", encoding="utf-8") as f:
                last_lines = deque(f, maxlen=50_000)

            output_file = os.path.join(settings.BASE_DIR, self.EXTRACT_DIR, 'output.csv')
            with open(output_file, "w", encoding="utf-8") as f:
                f.writelines(last_lines)

            csv_file_path = output_file

        print("CSV found at:", csv_file_path)
        self.search_index_service.create_index()
        total_imported = self.dump_to_database_service.save_to_database(
            site,
            self.fields_map,
            csv_file_path
        )

        shutil.rmtree(self.EXTRACT_DIR)
        os.remove(self.ZIP_FILE)

        return total_imported

    def _should_download_zip(self):
        if not os.path.exists(self.ZIP_FILE):
            return True

        creation_time = os.path.getctime(self.ZIP_FILE)
        creation_date = datetime.fromtimestamp(creation_time).date()
        today = datetime.today().date()

        if creation_date == today:
            return False

        return True

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
