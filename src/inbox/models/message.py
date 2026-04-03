from django.db import models
from src.inbox.models.conversation import Conversation

from automationapp import settings
from src.user.models import User as User


class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    message = models.TextField(null=True, blank=True)
    is_ready = models.BooleanField(default=True)
    file_info = models.JSONField(null=True, blank=True)
    file_type = models.CharField(max_length=10, null=True, blank=True)
    llm_reply = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def get_attachment_url(self) -> str | None:
        if self.file_info is None:
            return None

        return f"{settings.STORAGE_CDN_URL}/{self.file_info.get('file_path')}"

    def is_image(self):
        return self.file_type == 'image'

    def is_video(self):
        return self.file_type == 'video'

    def is_media_message(self):
        return self.is_image() or self.is_video()
