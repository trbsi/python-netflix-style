import random

from src.user.models import User
from src.user.services.post_registration.post_registration_service import PostRegistrationService


class CreateUserService:
    @staticmethod
    def create_random_user(username) -> User:
        if not username:
            username = random.randint(100000, 1000000)

        user = User.objects.create_user(
            username=f'{username}',
            email=f"{username}@email.top",
            password=f"{username}"
        )

        service = PostRegistrationService()
        service.post_register(user=user)

        return user

    @staticmethod
    def get_or_create(user_id: int):
        sender = User.objects.filter(username=user_id).first()
        if not sender:
            sender = CreateUserService.create_random_user(user_id)

        return sender
