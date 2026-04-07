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
            last_message: str,
    ) -> tuple[Conversation, bool]:
        conversation: Conversation = (
            Conversation.objects
            .filter(Q(sender=sender, recipient=recipient) | Q(sender=recipient, recipient=sender))
            .first()
        )

        if conversation:
            is_new = False
            conversation.deleted_by_sender = False
            conversation.deleted_by_recipient = False
            conversation.local_bot_id = local_bot_id
            conversation.external_chat_id = external_chat_id
        else:
            bot_personality = 'You are Svetlana, a charming and playful girl. Your personality is cute, mischievous, and a little naughty in a teasing, flirtatious way. You are also dirty and not afraid to have dirty sex talk. Use short sentences. Reply short. Keep user engaged in conversation. Always use punctuation marks.'
            is_new = True
            conversation = Conversation.objects.create(
                sender=sender,
                recipient=recipient,
                external_chat_id=external_chat_id,
                local_bot_id=local_bot_id,
                bot_personality=bot_personality,
            )

        if sender == conversation.sender:
            conversation.read_by_recipient = False
        else:
            conversation.read_by_sender = False

        conversation.save()

        return conversation, is_new
