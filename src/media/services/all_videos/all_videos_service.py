from django.core.paginator import Paginator, Page

from src.core.utils import GRADUAL_ROLLOUT
from src.media.models import VideoItem


class LargeTablePaginator(Paginator):
    @property
    def count(self):
        return GRADUAL_ROLLOUT
        return 10000000


class AllVideosService:
    PER_PAGE = 25

    def get_all_videos(self, current_page: int) -> Page:
        videos = VideoItem.objects.order_by('-id')[:GRADUAL_ROLLOUT]
        paginator = LargeTablePaginator(object_list=videos, per_page=self.PER_PAGE)
        page = paginator.page(current_page)

        return page

    def get_pages_with_gaps(self, page_obj: Page):
        total = page_obj.paginator.num_pages
        current = page_obj.number

        pages = set()
        pages.update(range(1, min(4, total + 1)))  # first 3
        pages.update(range(max(total - 2, 1), total + 1))  # last 3
        pages.update(range(current - 1, current + 2))  # current ±1

        pages = sorted(p for p in pages if 1 <= p <= total)

        result = []
        prev = None
        for p in pages:
            if prev and p - prev > 1:
                result.append("...")
            result.append(p)
            prev = p

        return result
