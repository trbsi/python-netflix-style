import bugsnag
from celery import shared_task

from src.chat.services.auto_reply.auto_reply_service import AutoReplyService


@shared_task
def auto_reply_task(
        message: str,
        chat_id: int,
        user_id: int,
        local_bot_id: str
) -> None:
    try:
        service = AutoReplyService()
        service.reply_now(message, chat_id, user_id, local_bot_id)
    except Exception as e:
        bugsnag.notify(e)
