from django.db import models


class SearchQuery(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True)
    raw_search_query = models.CharField(max_length=500)
    structured_search_query = models.CharField(max_length=500)

    objects = models.Manager()
