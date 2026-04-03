from src.inbox.models import Conversation
from src.user.models import User


class DeleteConversationService:
    def delete_conversations(self, ids: list, current_user: User) -> None:
        Conversation.objects.filter(id__in=ids, sender=current_user).update(deleted_by_sender=True)
        Conversation.objects.filter(id__in=ids, recipient=current_user).update(deleted_by_recipient=True)
