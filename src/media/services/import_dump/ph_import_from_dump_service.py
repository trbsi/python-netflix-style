import os
import re
import shutil
import zipfile
from collections import deque
from datetime import datetime

import requests
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.text import slugify

from automationapp import settings
from src.media.models import VideoItem, VideoCategory, VideoCategoryPivot
from src.media.services.manticore.manticore_service import ManticoreService


class PhImportFromDumpService:
    ZIP_URL = "https://www.pornhub.com/files/pornhub.com-db.zip"
    ZIP_FILE = "pornhub_db.zip"
    EXTRACT_DIR = "pornhub_data"

    def __init__(self):
        self.search_index_service = ManticoreService()

    def import_from_dump_locally(self):
        csv_file_path = os.path.join(settings.BASE_DIR, self.EXTRACT_DIR, 'output.csv')
        self.search_index_service.create_table()
        self._save_to_database(csv_file_path)

    def import_from_dump(self, import_all: bool = False):
        # 1. Download zip file
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
        # Create new file with last 100k rows
        if not import_all:
            with open(csv_file_path, "r", encoding="utf-8") as f:
                header = f.readline()
                last_lines = deque(f, maxlen=50_000)

            output_file = os.path.join(settings.BASE_DIR, self.EXTRACT_DIR, 'output.csv')
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(header)
                f.writelines(last_lines)

            csv_file_path = output_file

        self.search_index_service.create_table()
        self._save_to_database(csv_file_path)

        shutil.rmtree(self.EXTRACT_DIR)
        os.remove(self.ZIP_FILE)

    def _save_to_database(self, csv_file_path: str):
        print("Reading CSV...")
        videos_batch = 10_000
        categories_batch = 1000
        videos_array = []
        categories_array = []
        saved_videos = []
        pivots_to_create = []

        with open(csv_file_path, "r", encoding="utf-8", errors="ignore") as f:
            for index, line in enumerate(f):
                line = line.strip()
                fields = line.split("|")
                categories = fields[5]

                # VIDEOS
                video = VideoItem(
                    title=fields[3],
                    link='',
                    duration=fields[7],
                    thumb_small=fields[2],
                    thumb_large=fields[12],
                    embed_code=fields[0],
                    pub_date=timezone.now(),
                    tags=fields[4],
                    categories=categories,
                    site='pornhub',
                    external_id=self._get_external_id(fields[0]),
                    external_created_at=self._extract_created_at(fields[2])
                )
                videos_array.append(video)

                if len(videos_array) >= videos_batch:
                    saved_videos = self._insert_batch_videos(videos_array)
                    self.search_index_service.index_batch(saved_videos)
                    videos_array.clear()

                # CATEGORIES
                categories_split = categories.split(";")
                for category_label in categories_split:
                    slug = slugify(category_label)
                    video_category = VideoCategory(
                        slug=slug,
                        title=category_label,
                        image=f'images/categories/{slug}.jpg',
                    )
                    categories_array.append(video_category)

                    if len(categories_array) >= categories_batch:
                        self._insert_batch_categories(categories_array)
                        categories_array.clear()

                # VIDEO CATEGORY
                if saved_videos:
                    pivots_to_create = self._insert_video_category_pivot(pivots_to_create, saved_videos)
                    if len(pivots_to_create) >= videos_batch:
                        self._insert_batch_video_category(pivots_to_create)
                        pivots_to_create.clear()

            if videos_array:
                saved_videos = self._insert_batch_videos(videos_array)
                self.search_index_service.index_batch(saved_videos)

                pivots_to_create = self._insert_video_category_pivot(pivots_to_create, saved_videos)
                self._insert_batch_video_category(pivots_to_create)

                pivots_to_create.clear()
                videos_array.clear()

            if categories_array:
                self._insert_batch_categories(categories_array)
                categories_array.clear()

            if pivots_to_create:
                self._insert_batch_video_category(pivots_to_create)
                pivots_to_create.clear()

    def _insert_video_category_pivot(self, pivots_to_create: list, saved_videos: QuerySet[VideoItem]) -> list:
        categories_queryset = VideoCategory.objects.all()
        categories_map = {category.slug: category for category in categories_queryset}

        for saved_video in saved_videos:
            tmp_categories_array = saved_video.categories.split(";")
            for tmp_category_label in tmp_categories_array:
                slug = slugify(tmp_category_label)
                tmp_category = categories_map.get(slug)
                if tmp_category is None:
                    continue

                pivot = VideoCategoryPivot(
                    video_id=saved_video.id,
                    category_id=tmp_category.id
                )

                pivots_to_create.append(pivot)

        return pivots_to_create

    def _insert_batch_video_category(self, items: list[VideoCategoryPivot]) -> None:
        VideoCategoryPivot.objects.bulk_create(items, ignore_conflicts=True, batch_size=1000)

    def _insert_batch_categories(self, items: list[VideoCategory]) -> None:
        VideoCategory.objects.bulk_create(
            items,
            update_conflicts=True,
            batch_size=100,
            update_fields=['title', 'image']
        )

    def _insert_batch_videos(self, items: list[VideoItem]) -> QuerySet[VideoItem]:
        VideoItem.objects.bulk_create(items, ignore_conflicts=True, batch_size=1000)
        external_ids = [v.external_id for v in items]
        return VideoItem.objects.filter(external_id__in=external_ids)

    def _get_external_id(self, embed_code: str) -> str:
        match = re.search(r'/embed/([a-zA-Z0-9]+)', embed_code)
        if match:
            video_id = match.group(1)
            return video_id

        return ''

    def _extract_created_at(self, urls: str) -> datetime:
        url = urls.split(';')[0]
        match = re.search(r'/videos/(\d{6})/', url)

        yyyymm = match.group(1)
        return datetime.strptime(yyyymm, "%Y%m")
