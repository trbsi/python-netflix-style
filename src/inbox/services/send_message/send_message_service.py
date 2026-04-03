from django.db import transaction

from src.core.utils import format_datetime
from src.inbox.models import Message, Conversation
from src.user.models import User


class SendMessageService:
    @transaction.atomic
    def send_message(
            self,
            sender: User,
            conversation: Conversation,
            message_content: str | None,
    ) -> dict:
        file_info = None
        file_type = None

        message = Message.objects.create(
            sender=sender,
            conversation_id=conversation.id,
            message=message_content,
            file_info=file_info,
            file_type=file_type,
            is_ready=True if file_info is None else False
        )

        if sender == conversation.sender:
            conversation.read_by_recipient = False
        else:
            conversation.read_by_sender = False

        conversation.deleted_by_sender = False
        conversation.deleted_by_recipient = False
        conversation.save()

        if not message.is_ready:
            tmp_message = 'Preparing the media...'
        else:
            tmp_message = message.message

        return {
            'id': message.id,
            'created_at': format_datetime(message.created_at),
            'message': tmp_message,
            'attachment_url': None,
            'sender': {
                'id': message.sender.id,
                'profile_picture': message.sender.get_profile_picture(),
                'username': message.sender.username,
            }
        }
