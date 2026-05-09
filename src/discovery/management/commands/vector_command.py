from django.core.management.base import BaseCommand
from django.db import connection, connections
from sentence_transformers import SentenceTransformer

from src.discovery.models import VideoEmbeddings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test pgvector similarity with sample embeddings"

    def handle(self, *args, **options):
        with connections['postgresql'].cursor() as cursor:
            cursor.execute("""
                SELECT
                    video_id,
                    embedding <=> (
                        SELECT embedding
                        FROM discovery_videoembeddings
                        WHERE video_id = %s
                    ) AS distance
                FROM discovery_videoembeddings
                WHERE video_id != %s
                ORDER BY distance ASC;
            """, [1, 1])

            rows = cursor.fetchall()
            print(rows)
        return

        model = SentenceTransformer("BAAI/bge-small-en-v1.5")

        videos = [
            {
                "video_id": 1,
                "text": """
                Romantic amateur hotel encounter

                Categories:
                amateur, couples

                Tags:
                romantic, intimate, hotel, realistic

                Description:
                slow paced intimate couple encounter
                """
            },
            {
                "video_id": 2,
                "text": """
                Slow romantic couple weekend getaway

                Categories:
                amateur, couples

                Tags:
                romantic, intimate, vacation, hotel, realistic

                Description:
                soft paced intimate couple spending time together in hotel room during weekend trip
                """
            },
            {
                "video_id": 3,
                "text": """
                Realistic intimate hotel night with loving couple

                Categories:
                amateur, couples

                Tags:
                intimate, romantic, hotel, real chemistry, emotional

                Description:
                authentic couple interaction in hotel room with emotional connection and slow pacing
                """
            },
            {
                "video_id": 4,
                "text": """
                High intensity action combat training montage

                Categories:
                sports, fitness

                Tags:
                training, combat, strength, fast paced, athletic

                Description:
                explosive martial arts training session with heavy physical conditioning and speed drills
                """
            }
        ]

        # Clear old test data
        VideoEmbeddings.objects.using('postgresql').filter(
            video_id__in=[1, 2, 3, 4]
        ).delete()

        # Generate + store embeddings
        for v in videos:
            embedding = model.encode(v["text"])

            VideoEmbeddings.objects.using('postgresql').create(
                video_id=v["video_id"],
                embedding=embedding.tolist()
            )

        self.stdout.write(self.style.SUCCESS("Embeddings inserted successfully!"))
