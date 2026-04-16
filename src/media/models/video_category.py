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
        return self.category_search_url

    @property
    def category_search_url(self):
        kwargs = {'slug': self.slug}
        return reverse_lazy('media.categories_search', kwargs=kwargs)

    @property
    def categories_index_url(self):
        kwargs = {'slug': self.slug}
        return reverse_lazy('media.categories', kwargs=kwargs)
