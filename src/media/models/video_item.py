import hashlib
import random

from django.db import models
from django.urls import reverse_lazy
from django.utils.text import slugify

from src.core.utils import full_url_for_route


class VideoItem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    title_rewritten = models.TextField(null=True, blank=True)
    slug = models.SlugField(default='', max_length=100)
    slug_rewritten = models.SlugField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=300)
    duration = models.PositiveIntegerField(help_text="Duration in seconds")
    thumb_small = models.TextField()
    thumb_large = models.TextField()
    embed_code = models.TextField(help_text="Raw iframe HTML")
    site = models.CharField(max_length=20)
    external_id = models.CharField(max_length=50)
    external_created_at = models.DateField(null=True, blank=True)
    tags = models.TextField()
    categories = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=["link"]),
            models.Index(fields=['external_created_at']),
        ]

        constraints = [
            models.UniqueConstraint(fields=['external_id', 'site'], name='unique_videoitem_external_id_site'),
        ]

    def category_slugs(self):
        array = self.categories.split(",")
        result = []
        for category in array:
            if category:
                result.append(slugify(category))

        return result

    @property
    def video_url(self):
        slug = self.slug_rewritten if self.slug_rewritten else self.slug
        return reverse_lazy('media.single_video', kwargs={'id': self.id, 'slug': slug})

    @property
    def video_full_url(self):
        slug = self.slug_rewritten if self.slug_rewritten else self.slug
        return full_url_for_route('media.single_video', kwargs={'id': self.id, 'slug': slug})

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
        return self.external_created_at.strftime("%b %d, %Y")

    @property
    def categories_formatted(self):
        array = self.categories.split(",")
        return ' | '.join(array)

    @property
    def categories_array(self):
        array = self.categories.split(",")
        result = []
        for category in array:
            if category:
                result.append({'title': category, 'slug': slugify(category)})

        return result

    @property
    def thumbnail_large(self):
        return random.choice(self.thumb_large.split(','))

    @property
    def thumbnail_small(self):
        return random.choice(self.thumb_small.split(','))

    @property
    def main_title(self):
        return self.title_rewritten if self.title_rewritten else self.title
