from django.db import models


class TranslationBatch(models.Model):
    STATUS_STARTED = 'started'
    STATUS_FINISHED = 'finished'

    id = models.AutoField(primary_key=True)
    batch_id = models.CharField(max_length=100)
    status = models.CharField(max_length=15)
    last_id = models.IntegerField()
    batch_size = models.IntegerField(default=0)

    objects = models.Manager()
