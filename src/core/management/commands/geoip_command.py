import gzip
import io
import os
import shutil
import tarfile
from pathlib import Path

import requests
from django.utils import timezone
from requests import Response

from automationapp import settings
from src.core.management.commands.base_command import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not os.path.exists(settings.IP_DATABASE_PATH):
            os.makedirs(settings.IP_DATABASE_PATH, exist_ok=True)

        self._download_db_ip()

        self.success('Done.')

    def _download_maxmind(self):
        LICENSE_KEY = settings.MAX_MIND_LICENCE
        EDITION_ID = "GeoLite2-City"  # or "GeoLite2-Country", "GeoLite2-ASN"
        DOWNLOAD_DIR_TMP = "./geoip_tmp"
        output_path = settings.IP_DATABASE_PATH

        url = f"https://download.maxmind.com/app/geoip_download?edition_id={EDITION_ID}&license_key={LICENSE_KEY}&suffix=tar.gz"

        # --- Make download folder ---
        os.makedirs(DOWNLOAD_DIR_TMP, exist_ok=True)

        # --- Download the tar.gz ---
        print(f"Downloading {EDITION_ID} database...")
        r = requests.get(url, stream=True)
        r.raise_for_status()

        # --- Extract the tar.gz ---
        with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:gz") as tar:
            tar.extractall(path=DOWNLOAD_DIR_TMP)

        # --- Find .mmdb file in extracted directory ---
        mmdb_path = None
        for root, dirs, files in os.walk(DOWNLOAD_DIR_TMP):
            for file in files:
                if file.endswith(".mmdb"):
                    mmdb_path = os.path.join(root, file)
                    break
            if mmdb_path:
                break

        if os.path.exists(output_path):
            os.remove(output_path)
        shutil.move(mmdb_path, output_path)
        shutil.rmtree(DOWNLOAD_DIR_TMP)

    def _download_db_ip(self):
        now = timezone.now()
        year_month = f'{now.year}-{now.strftime('%m')}'
        url = f"https://download.db-ip.com/free/dbip-city-lite-{year_month}.mmdb.gz"
        gzip_path = Path(f'{settings.IP_DATABASE_BASE_PATH}/geoip-db.mmdb.gz')
        output_path = f'{settings.IP_DATABASE_PATH}'

        print(f'Downloading from {url}...')
        response: Response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(gzip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        print('Extracting...')
        with gzip.open(gzip_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        gzip_path.unlink()
