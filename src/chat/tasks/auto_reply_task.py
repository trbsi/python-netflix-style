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
        service.reply_now(
            last_message=message,
            chat_id=chat_id,
            user_id=user_id,
            local_bot_id=local_bot_id,
            send_to_bot=True
        )
    except Exception as e:
        bugsnag.notify(e)
