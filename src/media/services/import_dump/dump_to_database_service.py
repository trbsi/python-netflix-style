import csv
import random
import re
import sys
from datetime import datetime

import bugsnag
from django.db.models import QuerySet
from django.utils.text import slugify
from tqdm import tqdm

from src.core.utils import safe_get
from src.media.models import VideoItem, VideoCategory, VideoCategoryPivot
from src.media.services.manticore.manticore_service import ManticoreService


class DumpToDatabaseService:
    def __init__(self):
        self.search_index_service = ManticoreService()
        self.total_imported = 0

    def save_to_database(self, site: str, fields_map: dict, csv_file_path: str) -> int:
        print("Reading CSV for database insert...")
        csv.field_size_limit(sys.maxsize)
        videos_batch = 10_000
        categories_batch = 1000
        videos_array = []
        categories_array = []
        saved_videos = []
        pivots_to_create = []

        with open(csv_file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            total_rows = sum(1 for row in reader)
            print("Total rows:", total_rows)
            pbar = tqdm(total=total_rows)

            f.seek(0)  # reset to first line
            for index, line in enumerate(f):

                line = line.strip()
                fields = line.split(fields_map['fields_split_by'])

                if '<iframe' not in line:
                    continue

                try:
                    embed_code = self._embed_code(site, fields, fields_map).strip()
                    categories = self._get_categories(fields, fields_map)
                    external_created_at = self._extract_created_at(site, fields, fields_map)
                    duration = self._duration(site, fields, fields_map)
                    external_id = self._get_external_id(site, fields, fields_map)
                    title = self._get_safe_by_size(fields, fields_map['title'], 'title')
                    slug = self._slug(fields, fields_map)
                    link = self._get_safe_by_size(fields, fields_map['url'], 'link')

                    # VIDEOS
                    video = VideoItem(
                        title=title,
                        slug=slug,
                        link=link,
                        duration=duration,
                        thumb_small=fields[fields_map['thumb_small']],
                        thumb_large=fields[fields_map['thumb_large']],
                        embed_code=embed_code,
                        tags=fields[fields_map['tags']],
                        categories=categories,
                        site=site,
                        external_id=external_id,
                        external_created_at=external_created_at,
                    )
                    videos_array.append(video)
                except Exception as e:
                    exception = Exception(f'Exception: {str(e)}. Line: {line}')
                    bugsnag.notify(exception)
                    continue

                if len(videos_array) >= videos_batch:
                    saved_videos = self._insert_batch_videos(videos_array)
                    self.search_index_service.index_batch(saved_videos)
                    videos_array.clear()

                # CATEGORIES
                categories_split = categories.split(',')
                for category_label in categories_split:
                    category_label = category_label.strip()

                    # can be empty string categories
                    if not category_label or 'DO NOT USE' in category_label:
                        continue

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
                        saved_videos = None

                pbar.update(1)

            pbar.close()

            if videos_array:
                saved_videos = self._insert_batch_videos(videos_array)
                self.search_index_service.index_batch(saved_videos)

                pivots_to_create = self._insert_video_category_pivot(pivots_to_create, saved_videos)
                self._insert_batch_video_category(pivots_to_create)

                pivots_to_create.clear()
                videos_array.clear()
                saved_videos = None

            if categories_array:
                self._insert_batch_categories(categories_array)
                categories_array.clear()

            if pivots_to_create:
                self._insert_batch_video_category(pivots_to_create)
                pivots_to_create.clear()

        return self.total_imported

    def _insert_video_category_pivot(self, pivots_to_create: list, saved_videos: QuerySet[VideoItem]) -> list:
        categories_queryset = VideoCategory.objects.all()
        categories_map = {category.slug: category for category in categories_queryset}

        for saved_video in saved_videos:
            tmp_categories_array = saved_video.categories.split(',')
            for tmp_category_label in tmp_categories_array:
                # can be empty string categories
                if not tmp_category_label or 'DO NOT USE' in tmp_category_label:
                    continue

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
        VideoItem.objects.bulk_create(
            items,
            update_conflicts=True,
            batch_size=1000,
            update_fields=['title', 'link', 'duration', 'thumb_small', 'thumb_large', 'embed_code',
                           'external_created_at', 'tags', 'categories']
        )
        external_ids = [v.external_id for v in items]
        items = VideoItem.objects.filter(external_id__in=external_ids)

        self.total_imported += items.count()

        return items

    def _get_external_id(self, site: str, fields: list, fields_map: dict) -> str:
        external_id = fields[fields_map['external_id']]

        if site == 'pornhub':
            match = re.search(r'/embed/([a-zA-Z0-9]+)', external_id)
            if match:
                video_id = match.group(1)
                return video_id

        return external_id

    def _slug(self, fields: list, fields_map: dict) -> str:
        field = VideoItem._meta.get_field('slug')
        max_length = field.max_length

        slug = slugify(fields[fields_map['title']])

        if len(slug) > max_length:
            slug = slug[:max_length].rstrip("-")

        return slug if slug != '' else str(random.randint(1, 100000))

    def _get_safe_by_size(self, fields: list, index: int, database_field: str) -> str:
        value = safe_get(fields, index, '')
        field = VideoItem._meta.get_field(database_field)
        max_length = field.max_length if (field.max_length is not None) else 10_000

        if len(value) > max_length:
            return value[:max_length]

        return value

    def _extract_created_at(self, site: str, fields: list, fields_map: dict) -> datetime | None:
        data = safe_get(fields, fields_map['external_created_at'])

        if site == 'eporner':
            return datetime.now()

        if site == 'xvideos':
            return datetime.strptime(data, '%Y-%m-%d')

        if site == 'pornhub':
            url = data.split(';')[0]

            # Match year+month and day
            match = re.search(r'/videos/(\d{6})/(\d{1,2})/', url)
            if not match:
                return datetime(1970, 1, 1)

            try:
                yyyymm, day = match.groups()
                year = int(yyyymm[:4])
                month = int(yyyymm[4:6])
                day = int(day)
                return datetime(year, month, day)
            except Exception:
                return datetime(1970, 1, 1)

    def _embed_code(self, site: str, fields: list, fields_map: dict) -> str:
        embed_code = safe_get(fields, fields_map['embed_code'])
        id = safe_get(fields, fields_map['external_id'])

        if site == 'eporner':
            return f"""<iframe src="https://www.eporner.com/embed/{id}" width="640" height="360" frameborder="0" allowfullscreen></iframe>"""

        return embed_code

    def _get_categories(self, fields: list, fields_map: dict) -> str:
        categories = safe_get(fields, fields_map['categories'])
        categories = categories.split(fields_map['categories_split_by'])
        categories = [cat for cat in categories if len(cat) < 20]
        categories = categories[:4]
        categories = [cat.replace('_', ' ').replace('-', ' ').title() for cat in categories]
        categories = ','.join(categories)
        return categories

    def _duration(self, site, fields: list, fields_map: dict) -> str:
        duration = safe_get(fields, fields_map['duration'])
        if site == 'xvideos':
            duration = duration.strip(' sec')

        return duration
