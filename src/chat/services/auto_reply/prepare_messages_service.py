from src.inbox.models import Conversation, Message


class PrepareMessagesService:
    def get_chat_history(self, conversation: Conversation) -> list:
        messages = Message.objects.filter(conversation=conversation).order_by('-created_at', '-id')
        messages = list(messages[:10])[::-1]
        chat_history = []

        for message in messages:
            role = 'assistant' if message.sender.is_admin() else 'user'

            if chat_history and chat_history[-1]['role'] == role:
                chat_history[-1]['content'] = chat_history[-1]['content'].strip() + ' ' + message.message.strip()
            else:
                chat_history.append({'content': message.message, 'role': role})

        return chat_history
