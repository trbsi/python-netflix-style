from django.db import models

from src.user.models import User


class AgeVerification(models.Model):
    PROVIDER_DIDIT = 'didit.me'
    STATUS_VERIFIED = 'verified'

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)
    provider_session_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class AgeVerificationCountry(models.Model):
    id = models.BigAutoField(primary_key=True)
    country_code = models.CharField(max_length=5)
    country_name = models.CharField(max_length=50)
    state_code = models.CharField(max_length=10, null=True, blank=True)
    state_name = models.CharField(max_length=30, null=True, blank=True)
    is_age_verification_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['country_code', 'state_code', 'is_age_verification_required']),
        ]

    objects = models.Manager()
