from django.db import models

from src.user.models import User


class TikTokUser(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tiktok_username = models.CharField(max_length=100)
