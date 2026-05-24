import bugsnag
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from automationapp import settings
from src.notification.value_objects.push_notification_value_object import PushNotificationValueObject


class SlackService:
    # https://medium.com/@sizanmahmud08/how-to-integrate-slack-with-your-django-project-a-complete-step-by-step-guide-a7b1253cdcc3
    @staticmethod
    def send(notification: PushNotificationValueObject) -> None:
        client = WebClient(token=settings.SLACK_BOT_TOKEN)
        try:
            client.chat_postMessage(
                channel=settings.SLACK_CHANNEL_ID,
                text=notification.body
            )
        except SlackApiError as e:
            bugsnag.notify(e)
