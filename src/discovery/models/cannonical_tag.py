from django.db import models


class CanonicalTag(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    tag_group = models.CharField(max_length=100, null=True)
    is_gay = models.BooleanField(default=False)

    objects = models.Manager()
