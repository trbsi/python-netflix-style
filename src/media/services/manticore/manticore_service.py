from django.db import connections
from django.db.models import QuerySet

from src.media.models import VideoItem


class ManticoreService:
    def index_single(self, video: VideoItem):
        with connections['manticore'].cursor() as cursor:
            cursor.execute(f"""
               INSERT INTO videos_index
               (id, title, thumbnail, duration, categories)
               VALUES %s, %s, %s, %s
            """, [video.id, video.title, video.thumb_large, video.duration])

    def create_index(self):
        with connections['manticore'].cursor() as cursor:
            cursor.execute("""
               CREATE TABLE IF NOT EXISTS videos_index (
                   id BIGINT,
                   title TEXT,
                   thumbnail STRING,
                   duration INT,
                   categories TEXT
               )
               """)

    def reindex(self):
        with connections['manticore'].cursor() as cursor:
            cursor.execute("TRUNCATE TABLE videos_index")

        items = []
        batch = 10_000
        for item in VideoItem.objects.all().iterator(batch_size=batch):
            items.append(item)

            if len(items) >= batch:
                self.index_batch(items)
                items.clear()

            if items:
                self.index_batch(items)

    def index_batch(self, rows: list[VideoItem] | QuerySet[VideoItem]):
        with connections['manticore'].cursor() as cursor:
            values = ",".join(
                cursor.mogrify(
                    "(%s,%s,%s,%s,%s)",
                    (v.id, v.title, v.thumb_large, v.duration, ', '.join(v.category_slugs()))
                ).decode()
                for v in rows
            )

            sql = f"""
                   INSERT INTO videos_index
                   (id, title, thumbnail, duration, categories)
                   VALUES {values}
               """

            cursor.execute(sql)
