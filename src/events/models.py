from django.db import models


class Events(models.Model):
    id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=80)
    event_type = models.CharField(max_length=50)
    video_id = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    
    class Meta:
        indexes = [
            models.Index(fields=['event_type'], name='events_event_type_idx'),
            models.Index(fields=['video_id'], name='events_video_id_idx'),
        ]
