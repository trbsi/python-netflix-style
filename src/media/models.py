import hashlib

from django.db import models


class VideoItem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    link = models.URLField()
    duration = models.PositiveIntegerField(help_text="Duration in seconds")
    thumb = models.URLField()
    thumb_large = models.URLField()
    embed_code = models.TextField(help_text="Raw iframe HTML")
    pub_date = models.DateTimeField()
    site = models.CharField(max_length=20)
    external_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['external_id']),
        ]

    objects = models.Manager()

    @property
    def duration_formatted(self) -> str:
        h = self.duration // 3600
        m = (self.duration % 3600) // 60
        s = self.duration % 60

        if h > 0:
            return f"{h:02}:{m:02}:{s:02}"
        return f"{m:02}:{s:02}"

    @property
    def rating(self):
        seed = self.external_id or str(self.id)
        h = hashlib.md5(seed.encode()).hexdigest()
        return 3 + (int(h, 16) % 21) / 10  # 3.0 → 5.0

    @property
    def pub_date_formatted(self):
        return self.pub_date.strftime("%b %d, %Y")
