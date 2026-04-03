from django.db import models

from automationapp import settings
from src.user.models import User as User


class Conversation(models.Model):
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inbox_sender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inbox_recipient')
    last_message = models.TextField(null=True, blank=True)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_recipient = models.BooleanField(default=False)
    read_by_sender = models.BooleanField(default=False)
    read_by_recipient = models.BooleanField(default=False)
    is_automated = models.BooleanField(default=True)
    local_bot_id = models.CharField(max_length=20)
    bot_personality = models.TextField(null=True, blank=True)
    external_chat_id = models.CharField(max_length=20)
    external_last_id = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('sender', 'recipient'), name='conversation_unique_sender_recipient')
        ]

    def get_other_user(self, current_user: User) -> User:
        if current_user == self.sender:
            return self.recipient
        return self.sender

    def is_read(self, current_user: User) -> bool:
        if current_user == self.sender:
            return self.read_by_sender

        return self.read_by_recipient

    def get_creator(self) -> User:
        sender: User = self.sender
        if sender.is_creator():
            return self.sender

        return self.recipient

    def get_last_reply(self):
        """
        Return the latest Message in this conversation, or None if there are no messages.
        Uses the reverse relation `messages` defined on Message.conversation with related_name='messages'.
        messages is relation from Message model related_name='messages'
        """
        return self.messages.order_by('-id').first()

    def bot_token_from_id(self) -> str:
        return settings.TELEGRAM_BOTS[self.local_bot_id]['token']
