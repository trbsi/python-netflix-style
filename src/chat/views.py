import asyncio
import json

from django.http import HttpRequest, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from telegram import Update, Bot

from automationapp import settings
from src.chat.bot import TelegramBot
from src.chat.tasks import auto_reply_task

bot = TelegramBot()
app = bot.build_application()
_init_lock = asyncio.Lock()


@csrf_exempt
async def webhook(request: HttpRequest) -> JsonResponse:
    async with _init_lock:
        if not app._initialized:
            await app.initialize()

    data = json.loads(request.body.decode('utf-8'))
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return JsonResponse({"ok": True})


async def set_webhook(request: HttpRequest) -> JsonResponse:
    get = request.GET
    url = get.get('url')

    if url is None:
        url = f"{settings.APP_URL}{reverse_lazy('chat.webhook')}"

    bots = []
    for key, telegram_bot in settings.TELEGRAM_BOTS.items():
        bots.append(key)
        bot = Bot(telegram_bot['token'])
        await bot.set_webhook(url)

    return JsonResponse({"ok": True, 'url': url, 'bots': bots})


@require_GET
def test_reply(request: HttpRequest) -> JsonResponse:
    auto_reply_task.delay(message='hey ho', chat_id=8499962108, user_id=948373, local_bot_id='female_1')
    return JsonResponse({'success': True})
