from src.media.models import VideoItem


class SearchByCategoryService:
    def search_videos(self, slug: str):
        videos = VideoItem.objects.filter(categories_relation__slug=slug).order_by("-created_at")
        return videos
