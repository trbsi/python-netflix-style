import json
from pathlib import Path

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

from app import settings
from src.core.management.commands.base_command import BaseCommand


class Command(BaseCommand):
    help = 'Trains the chatbot model'

    def add_arguments(self, parser):
        parser.add_argument('--test', type=str, help="Some random sentence you want to get reply to", default=None)

    def handle(self, *args, **options):
        chatbot = ChatBot(settings.CHAT_BOT_NAME)
        test = options["test"]

        if test:
            self._test_output(chatbot, test)
            return

        trainer = ListTrainer(chatbot)

        conversations = f'{settings.BASE_DIR}/uploads/conversations.json'
        conversations = Path(conversations)
        if not conversations.exists():
            self.error('No conversations.json found in uploads folder')
            return

        with open(conversations, 'r') as conversations_file:
            conversations = json.load(conversations_file)

        train_conversations = []
        for index, conversation in enumerate(conversations):
            tmp = []
            print(f'Conversations count: {len(conversation)}')
            for message in conversation:
                tmp.append(message['content'])
            train_conversations.append(tmp)

        for conversation in train_conversations:
            trainer.train(conversation)

        self.success('Training complete')

    def _test_output(self, chatbot: ChatBot, test_output: str) -> None:
        response = chatbot.get_response(test_output)
        self.info(response.text)
