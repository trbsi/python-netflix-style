from django.db import transaction

from src.events.models import Events


class SaveEventService:
    EVENT_VIDEO = "video_view"
    EVENT_SEARCH = "search"

    @staticmethod
    def handle_event(session_id: str | None, event_type: str, metadata: dict):
        if event_type == SaveEventService.EVENT_SEARCH:
            return SaveEventService._handle_search(session_id, metadata)

        if event_type == SaveEventService.EVENT_VIDEO:
            return SaveEventService._handle_video_view(session_id, metadata)

        return SaveEventService._handle_default(session_id, event_type, metadata)

    @staticmethod
    def _handle_search(session_id: str | None, metadata: dict):
        if not session_id:
            return

        search_term = metadata.get("search_term")

        Events.objects.create(
            session_id=session_id,
            event_type=SaveEventService.EVENT_SEARCH,
            metadata={
                "search_term": search_term,
            },
        )

    @staticmethod
    @transaction.atomic
    def _handle_video_view(session_id: str | None, metadata: dict):
        if not session_id:
            return

        video_id = metadata.get("video_id")
        view_count = metadata.get("view_count", 1)

        event, created = Events.objects.select_for_update().get_or_create(
            video_id=video_id,
            event_type=SaveEventService.EVENT_VIDEO,
            defaults={
                "session_id": session_id,
                "metadata": {"view_count": view_count},
            },
        )

        if not created:
            metadata_obj = event.metadata or {}
            metadata_obj["view_count"] = metadata_obj.get("view_count", 0) + view_count

            event.session_id = session_id
            event.metadata = metadata_obj
            event.save(update_fields=["metadata", "session_id"])

    @staticmethod
    def _handle_default(session_id: str | None, event_type: str, metadata: dict):
        if not session_id:
            return

        Events.objects.create(
            session_id=session_id,
            event_type=event_type,
            metadata=metadata,
        )
