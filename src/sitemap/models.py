from django.db import models


# Create your models here.

class SitemapFile(models.Model):
    filename = models.CharField(max_length=255, unique=True)
    start_id = models.BigIntegerField()
    end_id = models.BigIntegerField()
    url_count = models.IntegerField()
    generated_at = models.DateTimeField(auto_now_add=True)
