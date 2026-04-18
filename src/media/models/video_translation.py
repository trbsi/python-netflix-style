from django.db import models


class VideoTranslation(models.Model):
    video = models.ForeignKey(
        'VideoItem',
        on_delete=models.CASCADE,
        related_name='translations'
    )
    # language code instead of FK (e.g. 'en', 'hr', 'es')
    language_code = models.CharField(max_length=10)
    # translated / localized fields
    title = models.TextField()
    slug = models.SlugField(max_length=120)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # one translation per language per video
            models.UniqueConstraint(
                fields=['video', 'language_code'],
                name='uniq_video_language_translation'
            ),

            # prevent slug collisions globally (important for routing)
            models.UniqueConstraint(
                fields=['slug'],
                name='uniq_translation_slug'
            ),
        ]
