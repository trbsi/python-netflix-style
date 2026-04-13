from django.core.paginator import Paginator, Page

from src.media.models import VideoItem


class LargeTablePaginator(Paginator):
    @property
    def count(self):
        return 10000000


class AllVideosService:
    PER_PAGE = 25

    def get_all_videos(self, current_page: int) -> Page:
        videos = VideoItem.objects.order_by('-id')
        paginator = LargeTablePaginator(object_list=videos, per_page=self.PER_PAGE)
        page = paginator.page(current_page)

        return page
