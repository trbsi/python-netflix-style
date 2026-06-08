from django.contrib import admin
from django.utils.safestring import mark_safe

from src.media.models.video_item import VideoItem


@admin.register(VideoItem)
class VideoItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'site', 'external_id']
    search_fields = ['title', 'external_id']
    readonly_fields = ['video_preview']
    fields = ['video_preview', 'video_metadata']

    def video_preview(self, obj):
        return mark_safe(obj.embed_code)

    video_preview.short_description = 'Video'
