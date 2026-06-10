import json
from collections import defaultdict

from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from src.discovery.models.tag_alias import TagAlias
from src.media.models.video_item import VideoItem


class PrettyJSONField(forms.JSONField):
    def prepare_value(self, value):
        if isinstance(value, str) or value in self.empty_values:
            return value

        return json.dumps(value, indent=2)


class VideoItemAdminForm(forms.ModelForm):
    video_metadata = PrettyJSONField(
        required=False,
        widget=forms.Textarea(attrs={'cols': 100, 'rows': 24}),
    )

    class Meta:
        model = VideoItem
        fields = '__all__'


@admin.register(VideoItem)
class VideoItemAdmin(admin.ModelAdmin):
    form = VideoItemAdminForm
    list_display = ['id', 'title_rewritten', 'site']
    list_filter = ['site']
    ordering = ['id']
    search_fields = ['title', 'external_id']
    readonly_fields = ['video_preview', 'tags_by_canonical']
    fields = ['video_preview', 'video_metadata', 'tags_by_canonical']

    def video_preview(self, obj):
        return mark_safe(obj.embed_code)

    video_preview.short_description = 'Video'

    def tags_by_canonical(self, obj):
        aliases = (
            TagAlias.objects
            .select_related('canonical_tag')
            .order_by('canonical_tag__slug', 'raw_tag')
        )

        grouped = defaultdict(list)
        for alias in aliases:
            grouped[alias.canonical_tag.slug].append(alias.raw_tag)

        if not grouped:
            return '-'

        lines = []
        for canonical, tags in sorted(grouped.items()):
            lines.append(f'<strong>{canonical}</strong>: {", ".join(tags)}')

        return mark_safe('<br>'.join(lines))

    tags_by_canonical.short_description = 'Tags by Canonical'
