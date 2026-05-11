from django.db import connections
from django.db.models import QuerySet

from src.discovery.models import VideoEmbeddings
from src.discovery.models.video_relationship import VideoRelationship


class VideoRelationshipsService():
    def generate_relationships(self):
        cursor = connections['postgresql'].cursor()
        videos: QuerySet[VideoEmbeddings] = (VideoEmbeddings.objects.using('postgresql')
                                             .order_by('id').iterator(chunk_size=1000))
        for video in videos:
            cursor.execute(
                f"""
                        SELECT 
                        video_id,
                        embedding <=> (SELECT embedding FROM discovery_videoembeddings WHERE video_id = %s) AS distance
                        FROM discovery_videoembeddings
                        WHERE video_id != %s
                        ORDER BY distance
                        LIMIT 10
                        """, [video.video_id, video.video_id]
            )

            related_videos = cursor.fetchall()

            # remove old relationships
            VideoRelationship.objects.using('postgresql').filter(video_id=video.video_id).delete()

            for vid in related_videos:
                VideoRelationship.objects.using('postgresql').create(
                    video_id=video.video_id,
                    related_video_id=vid[0],
                    similarity_score=vid[1],
                )
