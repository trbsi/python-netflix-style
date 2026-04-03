from src.inbox.models import InboxSettings
from src.user.models import User


class InboxSettingsService():
    def is_auto_reply_active(self, user: User) -> bool:
        settings = InboxSettings.objects.filter(user=user).first()
        if not settings:
            return True  # it is turned on by default

        return settings.auto_reply_active

    def update_settings(self, user: User, auto_reply_active: bool | None = None) -> InboxSettings:
        settings = InboxSettings.objects.filter(user=user).first()
        if not settings:
            settings = InboxSettings.objects.create(user=user)

        if auto_reply_active is not None:
            settings.auto_reply_active = auto_reply_active

        settings.save()

        return settings
