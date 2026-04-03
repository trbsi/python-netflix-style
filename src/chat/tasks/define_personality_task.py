from celery import shared_task

from src.chat.services.personality.personality_service import PersonalityService


@shared_task()
def define_personality_task(chat_id: int, user_id: int, local_bot_id: str, personality_message: str):
    service = PersonalityService()
    service.define_bot_personality(chat_id, user_id, local_bot_id, personality_message)
