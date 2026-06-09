from collections import defaultdict

from django.contrib import admin
from django.utils.safestring import mark_safe

from src.discovery.models.tag_alias import TagAlias
from src.media.models.video_item import VideoItem


@admin.register(VideoItem)
class VideoItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'site', 'external_id']
    search_fields = ['title', 'external_id']
    readonly_fields = ['video_preview', 'tags_by_canonical']
    fields = ['video_preview', 'video_metadata', 'tags_by_canonical']

    def video_preview(self, obj):
        return mark_safe(obj.embed_code)

    video_preview.short_description = 'Video'

    def tags_by_canonical(self, obj):
        raw_tags = [t.strip() for t in obj.tags.split(',') if t.strip()]
        if not raw_tags:
            return '-'

        aliases = (
            TagAlias.objects
            .filter(raw_tag__in=raw_tags)
            .select_related('canonical_tag')
        )

        grouped = defaultdict(list)
        for alias in aliases:
            tag = alias.canonical_tag.slug
            grouped[tag].append(alias.raw_tag)

        lines = []
        for canonical, tags in sorted(grouped.items()):
            lines.append(f'<strong>{canonical}</strong>: {", ".join(sorted(tags))}')

        return mark_safe('<br>'.join(lines))

    tags_by_canonical.short_description = 'Tags by Canonical'
