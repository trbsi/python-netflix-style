import os
import shutil
import zipfile
from collections import deque
from datetime import datetime

import requests

from automationapp import settings


class DownloadZipService:
    EXTRACT_DIR = "videos_dump_data"

    def download_zip(self, zip_url: str, zip_file: str, import_all: bool) -> str:
        if os.path.exists(self.EXTRACT_DIR):
            shutil.rmtree(self.EXTRACT_DIR)

            # 1. Download zip file
        if self._should_download_zip(zip_file):
            print("Downloading ZIP...")
            proxies = {}
            if settings.HTTP_PROXY:
                proxies = {
                    "http": settings.HTTP_PROXY,
                    "https": settings.HTTP_PROXY,
                }
            response = requests.get(zip_url, stream=True, proxies=proxies)
            response.raise_for_status()

            with open(zip_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print("Download complete.")
        else:
            print('ZIP file exists for today')

            # 2. Extract zip locally
        print("Extracting ZIP...")
        os.makedirs(self.EXTRACT_DIR, exist_ok=True)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
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

        return csv_file_path

    def _should_download_zip(self, zip_file: str):
        if not os.path.exists(zip_file):
            return True

        creation_time = os.path.getctime(zip_file)
        creation_date = datetime.fromtimestamp(creation_time).date()
        today = datetime.today().date()

        if creation_date == today:
            return False

        return True
