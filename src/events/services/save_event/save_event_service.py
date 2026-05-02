from typing import Optional, Dict, Any

from django.db import transaction

from src.events.models import Events


class SaveEventService:
    EVENT_VIDEO = 'video'
    EVENT_SEARCH = 'search'

    @staticmethod
    @transaction.atomic
    def save_event(
            session_id: str,
            event_type: str,
            video_id: Optional[int] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> Events:
        event = Events.objects.create(
            session_id=session_id,
            event_type=event_type,
            video_id=video_id,
            metadata=metadata or {},
        )
        return event

    @staticmethod
    def save_search_term(
            session_id: str | None,
            search_term: str,
    ) -> None:
        if not session_id:
            return
        SaveEventService.save_event(
            session_id=session_id,
            event_type=SaveEventService.EVENT_SEARCH,
            metadata={
                "search_term": search_term
            },
        )

    @staticmethod
    @transaction.atomic
    def save_video_view(
            session_id: str | None,
            video_id: int,
            view_count: int = 1,
    ) -> None:
        if not session_id:
            return

        event = (
            Events.objects
            .select_for_update()
            .filter(
                session_id=session_id,
                event_type=SaveEventService.EVENT_VIDEO,
                video_id=video_id,
            )
            .first()
        )

        if event:
            current_count = (event.metadata or {}).get("view_count", 0)
            event.metadata["view_count"] = current_count + view_count
            event.save(update_fields=["metadata"])

        SaveEventService.save_event(
            session_id=session_id,
            event_type="video_view",
            video_id=video_id,
            metadata={"view_count": view_count},
        )
