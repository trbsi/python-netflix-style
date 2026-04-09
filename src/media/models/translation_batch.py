from django.db import models


class TranslationBatch(models.Model):
    id = models.AutoField(primary_key=True)
    batch_id = models.CharField(max_length=100)
    status = models.CharField(max_length=15)
    last_id = models.IntegerField()

    objects = models.Manager()
