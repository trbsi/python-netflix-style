import hashlib
import random
from datetime import timezone

from django.db import models
from django.urls import reverse_lazy
from django.utils.text import slugify

from src.core.utils.lang import get_active_language
from src.core.utils.utils import full_url_for_route


class VideoItemQuerySet(models.QuerySet):
    def with_relations(self):
        return self.prefetch_related("translations_relation")


class VideoItemManager(models.Manager):
    def get_queryset(self):
        return VideoItemQuerySet(self.model, using=self._db).with_relations()


class VideoItem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    title_rewritten = models.TextField(null=True, blank=True)
    slug = models.SlugField(default='', max_length=100)
    slug_rewritten = models.SlugField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
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

    objects = VideoItemManager()

    class Meta:
        indexes = [
            models.Index(fields=["link"]),
            models.Index(fields=['external_created_at']),
            models.Index(fields=['slug_rewritten']),
        ]

        constraints = [
            models.UniqueConstraint(fields=['external_id', 'site'], name='unique_videoitem_external_id_site'),
        ]

    def category_slugs(self):
        array = self.categories.split(",")
        result = [slugify(category.strip()) for category in array]
        return result

    # for sitemap
    def get_absolute_url(self):
        return self.video_url

    def categories_and_tags(self) -> list:
        tags = self.tags.split(",")
        categories = [slugify(cat) for cat in self.categories.split(",")]
        return list(set(tags + categories))

    @property
    def video_url(self):
        kwargs = {'id': self.id, 'slug': self.main_slug}
        return reverse_lazy('media.single_video', kwargs=kwargs)

    @property
    def video_full_url(self):
        kwargs = {'id': self.id, 'slug': self.main_slug}
        return full_url_for_route('media.single_video', kwargs=kwargs)

    @property
    def duration_formatted(self) -> str:
        h = self.duration // 3600
        m = (self.duration % 3600) // 60
        s = self.duration % 60

        if h > 0:
            return f"{h:02}:{m:02}:{s:02}"
        return f"{m:02}:{s:02}"

    @property
    def duration_iso8601(self) -> str:
        h = self.duration // 3600
        m = (self.duration % 3600) // 60
        s = self.duration % 60

        parts = ["PT"]

        if h:
            parts.append(f"{h}H")
        if m:
            parts.append(f"{m}M")
        if s or (h == 0 and m == 0):
            parts.append(f"{s}S")

        return "".join(parts)

    @property
    def upload_date_iso(self):
        dt = self.created_at

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        dt = dt.astimezone(timezone.utc).replace(microsecond=0)

        return dt.isoformat()

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
                slug = slugify(category)
                result.append({
                    'title': category,
                    'slug': slug,
                    'category_search_url': reverse_lazy('media.categories_search', kwargs={'slug': slug}),
                })

        return result

    @property
    def thumbnail_large(self):
        return random.choice(self.thumb_large.split(','))

    @property
    def thumbnail_small(self):
        return random.choice(self.thumb_small.split(','))

    @property
    def main_title(self):
        lang = get_active_language()
        if lang != 'en':
            translation = self.translations_relation.filter(language_code=lang).first()
            if translation:
                return translation.title

        return self.title_rewritten if self.title_rewritten else self.title

    @property
    def main_description(self):
        lang = get_active_language()
        if lang != 'en':
            translation = self.translations_relation.filter(language_code=lang).first()
            if translation:
                return translation.description

        return self.description if self.description else ''

    @property
    def main_slug(self):
        lang = get_active_language()
        if lang != 'en':
            translation = self.translations_relation.filter(language_code=lang).first()
            if translation:
                return translation.slug

        return self.slug_rewritten if self.slug_rewritten else self.slug
