from django.db.models import Q

from src.inbox.models import Conversation
from src.user.models import User


class CreateConversationService:
    def get_or_create_conversation(
            self,
            sender: User,
            recipient: User,
            external_chat_id: int,
            local_bot_id: str,
    ) -> tuple[Conversation, bool]:
        conversation = (
            Conversation.objects
            .filter(Q(sender=sender, recipient=recipient) | Q(sender=recipient, recipient=sender))
            .first()
        )

        if conversation:
            is_new = False
            conversation.deleted_by_sender = False
            conversation.deleted_by_recipient = False
        else:
            is_new = True
            conversation = Conversation.objects.create(
                sender=sender,
                recipient=recipient,
                external_chat_id=external_chat_id,
                local_bot_id=local_bot_id,
            )

        if sender == conversation.sender:
            conversation.read_by_recipient = False
        else:
            conversation.read_by_sender = False

        conversation.save()

        return conversation, is_new
