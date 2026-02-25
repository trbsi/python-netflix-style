from django.db import models

from automationapp import settings
from src.user.models import User


class PostContent(models.Model):
    STATUS_UPLOADED = 'uploaded'
    STATUS_NONE = 'none'

    SITES = ['all', 'tiktok', 'facebook', 'linkedin', ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=20)  # video, image
    site = models.CharField(max_length=20)  # tiktok, facebook, all
    site_username = models.CharField(max_length=50)
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField()
    file_name = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    group = models.CharField(max_length=50,blank=True, null=True)

    objects = models.Manager()

    def is_tiktok(self):
        return self.site == 'tiktok'

    def is_facebook(self):
        return self.site == 'facebook'

    def is_linkedin(self):
        return self.site == 'linkedin'

    def is_all(self):
        return self.site == 'all'

    def get_file_path(self):
        return f'{settings.MEDIA_ROOT}/{self.file_name}'

    def get_file_url(self):
        return f'{settings.MEDIA_URL}{self.file_name}'

    def needs_proxy(self):
        return 'America' in self.timezone

    def is_video(self):
        return self.content_type == 'video'


class SocialAccount(models.Model):
    TIKTOK = 'tiktok'
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    site = models.CharField(max_length=20)  # tiktok, facebook
