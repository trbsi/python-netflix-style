from datetime import timezone, datetime

from src.inbox.models import Message


class IdleMessagingService:
    IDLE_MESSAGE_TIME_DELTA_MINUTES = 15

    def is_messaging_idle(self):
        message: None | Message = Message.objects.order_by('-id').first()
        if message is None:
            return True

        now = datetime.now(timezone.utc).timestamp()
        message_time = message.created_at.timestamp()
        referent_time_in_seconds = self.IDLE_MESSAGE_TIME_DELTA_MINUTES * 60

        if (now - message_time) < referent_time_in_seconds:
            return False

        return True
