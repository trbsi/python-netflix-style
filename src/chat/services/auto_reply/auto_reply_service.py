import asyncio
import random

import bugsnag
from telegram import Bot

from automationapp import settings
from src.chat.services.auto_reply.commercial_llm_reply_service import CommercialLLMReplyService
from src.chat.services.auto_reply.split_sentences_service import SplitSentencesService
from src.inbox.models import Conversation
from src.inbox.services.create_conversation.create_conversation_service import CreateConversationService
from src.inbox.services.send_message.send_message_service import SendMessageService
from src.user.models import User
from src.user.services.create_user.create_user_service import CreateUserService


class AutoReplyService:
    def __init__(self):
        self.commercial_llm_service = CommercialLLMReplyService()
        self.create_conversation_service = CreateConversationService()
        self.send_message_service = SendMessageService()
        self.split_sentences_service = SplitSentencesService()

    def reply_now(
            self,
            last_message: str,
            chat_id: int | str,
            user_id: int | str,
            local_bot_id: str,
            send_to_bot: bool,
            admin_id: int | str = None
    ) -> list:
        print('AUTO REPLY', chat_id, user_id)
        try:
            if not admin_id:
                admin = User.get_admin()
            else:
                admin = CreateUserService.get_or_create(admin_id)

            sender = CreateUserService.get_or_create(user_id)
            conversation, is_new = self.create_conversation_service.get_or_create_conversation(
                sender=sender,
                recipient=admin,
                external_chat_id=chat_id,
                local_bot_id=local_bot_id,
                last_message=last_message
            )
            self.send_message_service.send_message(sender, conversation, last_message)

            if settings.REMOTE_LLM:
                sentence = self.commercial_llm_service.get_remote_reply(conversation, last_message, is_new)
            else:
                raise Exception('No other LLM is set for reply')

            sentences = self._prepare_messages(sentence, admin, conversation)
            if send_to_bot:
                asyncio.run(self._send(sentences, chat_id, conversation))

            return sentences
        except Exception as e:
            bugsnag.notify(e)
            return []

    def _prepare_messages(
            self,
            sentence: str,
            admin: User,
            conversation: Conversation,
    ) -> list:
        sentences = self.split_sentences_service.split_sentences(sentence)

        for sentence in sentences:
            # admin is sending a message
            self.send_message_service.send_message(
                sender=admin,
                conversation=conversation,
                message_content=sentence
            )

        conversation.last_message = sentences[-1]
        conversation.save()

        return sentences

    async def _send(
            self,
            sentences: list,
            chat_id: int,
            conversation: Conversation
    ) -> None:
        bot = Bot(token=conversation.bot_token_from_id())
        for sentence in sentences:
            last_message = sentence
            await asyncio.sleep(random.randint(1, 5))
            await bot.send_message(chat_id=chat_id, text=last_message)
