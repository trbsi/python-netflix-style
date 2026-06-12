from src.media_discovery.models import Tag


class SearchTagsService:
    limit = 10

    def search_tags(self, tag: str | None) -> list[dict]:
        if not tag:
            return []

        tag = tag.strip()
        if not tag:
            return []

        tags = (
            Tag.objects
            .filter(is_in_use=True, name__icontains=tag)
            .order_by('name')
            .values('id', 'name')[:self.limit]
        )

        return list(tags)
