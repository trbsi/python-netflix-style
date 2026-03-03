import hashlib
import random

from django.db import models
from django.utils.text import slugify


class VideoCategory(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    slug = models.SlugField()
    image = models.CharField(max_length=20)

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
        ]


class VideoItem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    link = models.URLField()
    duration = models.PositiveIntegerField(help_text="Duration in seconds")
    thumb_small = models.TextField()
    thumb_large = models.TextField()
    embed_code = models.TextField(help_text="Raw iframe HTML")
    pub_date = models.DateTimeField()
    site = models.CharField(max_length=20)
    external_id = models.CharField(max_length=50)
    tags = models.TextField()
    categories = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    categories_relation = models.ManyToManyField(
        VideoCategory,
        through="VideoCategoryPivot",
        related_name="videos"
    )

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

    @property
    def categories_formatted(self):
        array = self.categories.split(";")
        return ' | '.join(array)

    @property
    def categories_array(self):
        array = self.categories.split(";")
        result = []
        for category in array:
            result.append({'title': category, 'slug': slugify(category)})

        return result

    @property
    def thumbnail_large(self):
        return random.choice(self.thumb_large.split(';'))

    @property
    def thumbnail_small(self):
        return random.choice(self.thumb_small.split(';'))


class VideoCategoryPivot(models.Model):
    video = models.ForeignKey(
        VideoItem,
        on_delete=models.CASCADE,
        related_name="video_category_links"
    )
    category = models.ForeignKey(
        VideoCategory,
        on_delete=models.CASCADE,
        related_name="video_category_links"
    )

    class Meta:
        unique_together = ("video", "category")
        indexes = [
            models.Index(fields=["category", "video"]),
            models.Index(fields=["video"]),
        ]
