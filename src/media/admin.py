import json

from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

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
    list_display = ['id', 'title', 'site', 'external_id']
    search_fields = ['title', 'external_id']
    readonly_fields = ['video_preview']
    fields = ['video_preview', 'video_metadata']

    def video_preview(self, obj):
        return mark_safe(obj.embed_code)

    video_preview.short_description = 'Video'
