from django.db import models


class VideoCategory(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    image = models.CharField(max_length=20)

    objects = models.Manager()
