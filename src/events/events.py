from src.events.services.save_event.save_event_service import SaveEventService
from src.events.tasks import store_event_task


def enqueue_search_event(session_id: str | None, search_term: str):
    store_event_task.delay(
        SaveEventService.EVENT_SEARCH,
        session_id,
        {
            "search_term": search_term,
        },
    )


def enqueue_video_view_event(session_id: str | None, video_id: int):
    store_event_task.delay(
        SaveEventService.EVENT_VIDEO,
        session_id,
        {
            "video_id": video_id,
            "view_count": 1,
        },
    )
