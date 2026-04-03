from django.urls import reverse_lazy
from telegram import Bot

from automationapp import settings
from src.core.management.commands.base_command import BaseCommand


class Command(BaseCommand):
    help = 'Set webhook command'

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, nargs='?', default=None)

    async def handle(self, *args, **options):
        url = options['url']
        if url is None:
            url = f"{settings.APP_URL}{reverse_lazy('chat.webhook')}"

        for key, telegram_bot in settings.TELEGRAM_BOTS.items():
            bot = Bot(telegram_bot['token'])
            await bot.set_webhook(url)
        self.info(f'Webhook set successfully to {url}')
