from unittest.mock import patch, AsyncMock

from django.test import TestCase
from django.urls import reverse

from src.inbox.models import Conversation, Message
from src.user.models import User


class AutoReplyTest(TestCase):
    @patch('src.chat.services.auto_reply.auto_reply_service.Bot')
    def test_auto_reply(self, MockBot):
        username = 948373
        mock_bot_instance = MockBot.return_value
        mock_bot_instance.send_message = AsyncMock()

        User.objects.create_superuser(username='test', password='aaa', email='t@t.com')

        response = self.client.get(reverse('chat.test_reply'))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(data, {'success': True})

        mock_bot_instance.send_message.assert_awaited()

        conversation = Conversation.objects.filter(sender__username=username).first()
        self.assertEqual(Conversation.objects.filter(sender__username=username).count(), 1)
        self.assertGreater(Message.objects.filter(conversation_id=conversation.id).count(), 1)
        self.assertEqual(User.objects.filter(username=username).count(), 1)
