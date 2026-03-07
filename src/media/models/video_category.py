from django.db import models


class VideoCategory(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=50)
    image = models.CharField(max_length=100)

    objects = models.Manager()
