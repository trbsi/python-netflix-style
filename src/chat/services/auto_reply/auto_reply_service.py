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

    def reply_now(self, last_message: str, chat_id: int, user_id: int, local_bot_id: str) -> None:
        print('AUTO REPLY', chat_id, user_id)
        try:
            admin = User.get_admin()
            sender = CreateUserService.get_or_create(user_id)
            conversation, is_new = self.create_conversation_service.get_or_create_conversation(
                sender=sender,
                recipient=admin,
                external_chat_id=chat_id,
                local_bot_id=local_bot_id,
            )
            self.send_message_service.send_message(sender, conversation, last_message)

            if settings.REMOTE_LLM:
                sentence = self.commercial_llm_service.get_remote_reply(conversation, last_message, is_new)
            else:
                raise Exception('No other LLM is set for reply')

            self._prepare_and_send_messages(sentence, chat_id, admin, conversation)
        except Exception as e:
            bugsnag.notify(e)

    def _prepare_and_send_messages(
            self,
            sentence: str,
            chat_id: int,
            admin: User,
            conversation: Conversation,
    ):
        sentences = self.split_sentences_service.split_sentences(sentence)
        number_of_sentences = len(sentences)

        for i in range(number_of_sentences):
            # admin is sending a message
            self.send_message_service.send_message(
                sender=admin,
                conversation=conversation,
                message_content=sentences[i]
            )

        conversation.last_message = sentences[number_of_sentences - 1]
        conversation.save()

        asyncio.run(self._send(sentences, chat_id, number_of_sentences, conversation))

    async def _send(
            self,
            sentences: list,
            chat_id: int,
            number_of_sentences: int,
            conversation: Conversation
    ) -> None:
        bot = Bot(token=conversation.bot_token_from_id())
        for i in range(number_of_sentences):
            last_message = sentences[i]
            await asyncio.sleep(random.randint(1, 5))
            await bot.send_message(chat_id=chat_id, text=last_message)
