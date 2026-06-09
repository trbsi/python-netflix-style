import uuid

from django.core import signing

from src.discovery.models import SearchQuery, TagAlias
from src.events.events import enqueue_search_event


class PersonalizeSiteService():
    def personalize_site(self, text: str, selected_tag_ids: str | list, session_id: str | None) -> str | None:
        tag_ids = self._normalize_tag_ids(selected_tag_ids)
        if not tag_ids:
            return None

        tags = list(
            TagAlias.objects
            .filter(id__in=tag_ids)
            .order_by('raw_tag')
            .values_list('raw_tag', flat=True)
        )
        if not tags:
            return None

        search_text = ', '.join(tags)
        enqueue_search_event(session_id, search_text)

        uuid_str = str(uuid.uuid4())
        SearchQuery.objects.create(
            uuid=uuid_str,
            raw_search_query=search_text,
            structured_search_query=','.join(tags),
            search_type=SearchQuery.SEARCH_TYPE_TAGS
        )

        return signing.dumps({
            "query": search_text,
            "id": uuid_str,
        })

    def _normalize_tag_ids(self, selected_tag_ids: str | list) -> list[int]:
        if not selected_tag_ids:
            return []

        if isinstance(selected_tag_ids, str):
            selected_tag_ids = selected_tag_ids.split(',')

        tag_ids = []
        for tag_id in selected_tag_ids:
            try:
                tag_ids.append(int(tag_id))
            except (TypeError, ValueError):
                continue

        return list(dict.fromkeys(tag_ids))
