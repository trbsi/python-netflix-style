from django.db.models import QuerySet
from sentence_transformers import SentenceTransformer

from src.discovery.models import VideoEmbeddings
from src.media.models import VideoItem


class VectorizeVideosService():
    def vectorize_videos(self):
        videos: QuerySet[VideoItem] = VideoItem.objects.iterator(chunk_size=1000)
        model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        for video in videos:
            text = f"""
            Title:
            {video.title}
            
            Categories:
            {video.categories}
            
            Tags:
            {video.tags}
            """

            embeddings = model.encode(text)
            VideoEmbeddings.objects.using('postgresql').create(
                video_id=video.id,
                embeddings=embeddings.tolist()
            )
