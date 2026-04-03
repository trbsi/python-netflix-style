from src.inbox.services.create_conversation.create_conversation_service import CreateConversationService
from src.user.models import User


class PersonalityService:
    def __init__(self):
        self.create_conversation_service = CreateConversationService()

    def define_bot_personality(
            self,
            chat_id: int,
            user_id: int,
            local_bot_id: str,
            personality_message: str
    ) -> None:
        admin = User.get_admin()
        sender = User.get_or_create(user_id)
        conversation, is_new = self.create_conversation_service.get_or_create_conversation(
            sender=sender,
            recipient=admin,
            external_chat_id=chat_id,
            local_bot_id=local_bot_id,
        )

        conversation.bot_personality = personality_message
        conversation.save()
