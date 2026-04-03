from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse_lazy

from automationapp import settings
from src.user.enum import UserEnum
from src.user.services.create_user.create_user_service import CreateUserService


# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True, blank=False, null=False, validators=[RegexValidator(
        r'^[0-9a-zA-Z]*$',
        'Username must contain only letters and numbers.'
    )])
    email = models.EmailField(unique=True)

    def get_profile_picture(self):
        profile_image = str(self.profile.profile_image)
        if profile_image != '' and profile_image is not None:
            return settings.MEDIA_URL + profile_image

        return f"https://ui-avatars.com/api/?name={self.username}"

    def is_regular_user(self):
        return self.groups.filter(name=UserEnum.ROLE_USER.value).exists()

    def is_creator(self):
        return self.groups.filter(name=UserEnum.ROLE_CREATOR.value).exists()

    def get_role(self) -> str:
        return self.groups.first().name

    def get_profile_url(self) -> str:
        return reverse_lazy('user.profile', kwargs={'username': self.username})

    def is_admin(self):
        return self.is_superuser

    @staticmethod
    def get_admin():
        return User.objects.filter(is_superuser=True).first()

    @staticmethod
    def get_or_create(user_id: int):
        sender = User.objects.filter(username=user_id).first()
        if not sender:
            sender = CreateUserService.create_random_user(user_id)

        return sender
