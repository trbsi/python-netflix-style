from src.inbox.services.create_conversation.create_conversation_service import CreateConversationService
from src.user.models import User
from src.user.services.create_user.create_user_service import CreateUserService


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
        print('PERSONALITY MESSAGE', personality_message)
        admin = User.get_admin()
        sender = CreateUserService.get_or_create(user_id)
        conversation, is_new = self.create_conversation_service.get_or_create_conversation(
            sender=sender,
            recipient=admin,
            external_chat_id=chat_id,
            local_bot_id=local_bot_id,
        )

        conversation.bot_personality = personality_message
        conversation.external_last_id = None
        conversation.save()
