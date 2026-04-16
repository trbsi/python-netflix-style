from django.db import models
from django.urls import reverse_lazy
from django.utils import translation


class VideoCategory(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=50)
    image = models.CharField(max_length=100)

    objects = models.Manager()

    # for sitemap
    def get_absolute_url(self):
        lang = translation.get_language()
        kwargs = {'slug': self.slug, 'lang': lang}
        return reverse_lazy('media.categories_search', kwargs=kwargs)

    @property
    def category_search_url(self):
        lang = translation.get_language()
        kwargs = {'slug': self.slug, 'lang': lang}
        return reverse_lazy('media.categories_search', kwargs=kwargs)

    @property
    def categories_index_url(self):
        lang = translation.get_language()
        kwargs = {'slug': self.slug, 'lang': lang}
        return reverse_lazy('media.categories', kwargs=kwargs)
