from src.media_discovery.models import Tag


class SearchTagsService:
    limit = 10

    def search_tags(self, tag: str | None, tag_groups: list[str] | None = None) -> list[dict]:
        if not tag:
            return []

        tag = tag.strip()
        if not tag:
            return []

        query = Tag.objects.filter(name__icontains=tag)
        if isinstance(tag_groups, list) and tag_groups:
            query = query.filter(group__in=tag_groups)

        tags = (
            query
            .order_by('name')
            .values('id', 'name')[:self.limit]
        )

        return list(tags)
