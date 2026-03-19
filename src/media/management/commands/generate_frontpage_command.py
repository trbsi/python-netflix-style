import time

from src.core.management.commands.base_command import BaseCommand
from src.media.services.frontpage.frontpage_service import FrontpageService
from src.notification.services.notification_service import NotificationService
from src.notification.value_objects.push_notification_value_object import PushNotificationValueObject


class Command(BaseCommand):
    def handle(self, *args, **options):
        start = time.time()

        service = FrontpageService()
        ids_length = service.generate_frontpage()

        end = time.time()
        minutes = (end - start) / 60
        message = f"GenerateFrontpageCommand. Execution time: {minutes:.2f} minutes. Total ids: {ids_length}"
        print(message)

        push = PushNotificationValueObject(body=message)
        NotificationService.send_notification(push)
