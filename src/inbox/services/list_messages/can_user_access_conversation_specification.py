from django.db.models import Q

from src.inbox.models import Conversation
from src.user.models import User


class CanUserAccessConversationSpecification:
    def check(self, conversation_id: int, user: User) -> bool:
        return (
            Conversation
            .objects
            .filter(
                Q(id=conversation_id) & (Q(sender=user) | Q(recipient=user))
            )
            .exists()
        )
