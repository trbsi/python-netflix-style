from django.db import models


class SystemMessage(models.Model):
    TYPE_GPU_CREATING = 'creating_gpu'
    TYPE_GPU_CREATED = 'created_gpu'
    TYPE_GPU_NOT_AVAILABLE = 'gpu_not_available'

    id = models.BigAutoField(primary_key=True)
    message = models.CharField(max_length=255)
    message_type = models.CharField(max_length=30)

    objects = models.Manager()
