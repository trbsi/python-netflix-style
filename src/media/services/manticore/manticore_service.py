from django.db import connections

from src.media.models import VideoItem


class ManticoreService:
    def index_single(self, video: VideoItem):
        with connections['manticore'].cursor() as cursor:
            cursor.execute(f"""
               INSERT INTO videos_index
               (id, title, thumbnail, duration)
               VALUES %s, %s, %s, %s
            """, [video.id, video.title, video.thumb_large, video.duration])

    def create_index(self):
        with connections['manticore'].cursor() as cursor:
            cursor.execute("""
               CREATE TABLE IF NOT EXISTS videos_index (
                   id BIGINT,
                   title TEXT,
                   thumbnail STRING,
                   duration INT
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
                self.insert_batch(items)
                items.clear()

            if items:
                self.insert_batch(items)

    def insert_batch(self, rows: list[VideoItem]):
        with connections['manticore'].cursor() as cursor:
            values = ",".join(
                cursor.mogrify(
                    "(%s,%s,%s,%s)",
                    (v.id, v.title, v.thumb_large, v.duration)
                ).decode()
                for v in rows
            )

            sql = f"""
                   INSERT INTO videos_index
                   (id, title, thumbnail, duration)
                   VALUES {values}
               """

            cursor.execute(sql)
