import asyncio

from django.db.models import QuerySet
from telegram import Bot

from src.core.management.commands.base_command import BaseCommand
from src.inbox.models import Conversation


class Command(BaseCommand):
    help = 'Find conversations which require chatbot to reply and reply to them'

    def handle(self, *args, **options):
        conversations: QuerySet[Conversation] = Conversation.objects.filter(last_reply_from='bot')
        print('Number of conversations: ', conversations.count())

        for conversation in conversations:
            asyncio.run(self._send_message(conversation))

    async def _send_message(self, conversation: Conversation):
        bot = Bot(token=conversation.bot_token_from_id())
        await bot.send_message(
            chat_id=conversation.external_chat_id,
            text=system_message.message
        )
