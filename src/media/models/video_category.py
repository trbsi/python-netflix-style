from django.db import models
from django.urls import reverse_lazy


class VideoCategory(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=50)
    image = models.CharField(max_length=100)

    objects = models.Manager()

    # for sitemap
    def get_absolute_url(self):
        return reverse_lazy('media.categories_search', kwargs={'slug': self.slug})
