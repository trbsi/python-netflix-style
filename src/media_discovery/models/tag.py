from django.db import models


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    group = models.CharField(max_length=20)
    is_in_use = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["is_in_use"]),
            models.Index(fields=["group"]),
            models.Index(fields=["name"]),
            models.Index(fields=["group", "name"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["group", "name"], name="unique_media_discovery_tag_group_name"),
        ]

    def __str__(self):
        return f"{self.group}:{self.name}"
