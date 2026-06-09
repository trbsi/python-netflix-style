from src.discovery.models import TagAlias


class SearchTagsService:
    limit = 10

    def search_tags(self, tag: str | None) -> list[dict]:
        if not tag:
            return []

        tag = tag.strip()
        if not tag:
            return []

        tags = (
            TagAlias.objects
            .filter(raw_tag__istartswith=tag)
            .order_by('raw_tag')
            .values('id', 'raw_tag')[:self.limit]
        )

        return list(tags)
