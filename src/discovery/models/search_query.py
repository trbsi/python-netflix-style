from django.db import models


class SearchQuery(models.Model):
    SEARCH_TYPE_RAW = 'raw'
    SEARCH_TYPE_TAGS = 'tags'

    id = models.AutoField(primary_key=True)
    uuid = models.CharField(max_length=36, unique=True)
    raw_search_query = models.CharField(max_length=500)
    structured_search_query = models.CharField(max_length=500)
    search_type = models.CharField(max_length=20, default='raw')

    objects = models.Manager()
