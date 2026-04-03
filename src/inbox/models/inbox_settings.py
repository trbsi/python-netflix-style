from django.db import models

from src.user.models import User as User


class InboxSettings(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auto_reply_active = models.BooleanField(default=False)
