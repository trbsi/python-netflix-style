import bugsnag
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters, Application,
)

from automationapp import settings
from src.chat.tasks import auto_reply_task, define_personality_task


class TelegramBot:
    BOT = settings.TELEGRAM_BOTS[settings.DEFAULT_BOT]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = update.effective_chat.id
            await context.bot.send_message(
                chat_id=chat_id,
                text="hello you cutie pie. what's up?"
            )
        except Exception as e:
            bugsnag.notify(e)

    async def send(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = update.effective_chat.id
            user_id = update.effective_user.id
            text = update.message.text
            auto_reply_task.delay(text, chat_id, user_id, self.BOT['id'])
        except Exception as e:
            bugsnag.notify(e)

    async def personality_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        # everything after /personality split by spaces
        text = " ".join(context.args)

        if not text:
            await context.bot.send_message(chat_id=chat_id, text="Usage: /personality <text>")
            return

        define_personality_task.delay(chat_id, user_id, self.BOT['id'], text)

    def build_application(self) -> Application:
        app = ApplicationBuilder().token(self.BOT['token']).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.send))
        app.add_handler(CommandHandler("personality", self.personality_command))

        return app
