from celery import shared_task

from src.events.services.save_event.save_event_service import SaveEventService


@shared_task
def store_event_task(event_type: str, session_id: str | None, metadata: dict | None = None):
    SaveEventService.handle_event(
        session_id=session_id,
        event_type=event_type,
        metadata=metadata or {},
    )
