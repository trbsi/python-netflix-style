from src.inbox.models import Conversation
from src.user.models import User


class ReadConversationService:
    def read_conversation(self, conversation_id, user: User) -> Conversation:
        conversation = Conversation.objects.get(id=conversation_id)

        if conversation.sender == user:
            conversation.read_by_sender = True
            conversation.save()
        else:
            conversation.read_by_recipient = True
            conversation.save()

        return conversation
