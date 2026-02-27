import os
import re
import zipfile

import requests
from django.utils import timezone

from automationapp import settings
from src.media.models import VideoItem


class PhImportFromDumpService:
    ZIP_URL = "https://www.pornhub.com/files/pornhub.com-db.zip"
    ZIP_FILE = "pornhub_db.zip"
    EXTRACT_DIR = "pornhub_data"

    def import_from_dump_locally(self):
        csv_file_path = os.path.join(settings.BASE_DIR, self.EXTRACT_DIR, 'output.csv')
        self._save_to_database(csv_file_path)

    def import_from_dump(self):
        # 1. Download zip file
        print("Downloading ZIP...")
        response = requests.get(self.ZIP_URL, stream=True)
        response.raise_for_status()

        with open(self.ZIP_FILE, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("Download complete.")

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
                if file.endswith(".csv"):
                    csv_file_path = os.path.join(root, file)
                    break

        if not csv_file_path:
            raise Exception("CSV file not found after extraction.")

        print("CSV found at:", csv_file_path)
        self._save_to_database(csv_file_path)

    def _save_to_database(self, csv_file_path: str):
        print("Reading CSV...")
        with open(csv_file_path, "r", encoding="utf-8", errors="ignore") as f:
            for index, line in enumerate(f):
                line = line.strip()
                fields = line.split("|")

                if (settings.APP_ENV != 'production' and index > 100):
                    break

                external_id = self._get_external_id(fields[0])
                if VideoItem.objects.filter(external_id=external_id).exists():
                    continue

                VideoItem.objects.create(
                    title=fields[3],
                    link='',
                    duration=fields[7],
                    thumb_small=fields[2],
                    thumb_large=fields[12],
                    embed_code=fields[0],
                    pub_date=timezone.now(),
                    tags=fields[4],
                    categories=fields[5],
                    site='pornhub',
                    external_id=external_id
                )

    def _get_external_id(self, embed_code: str) -> str:
        match = re.search(r'/embed/([a-zA-Z0-9]+)', embed_code)
        if match:
            video_id = match.group(1)
            return video_id

        return ''
