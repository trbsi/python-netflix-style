import random

import bugsnag
from django.http import HttpRequest
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from automationapp import settings
from src.notification.services.notification_service import NotificationService
from src.notification.value_objects.email_value_object import EmailValueObject
from src.notification.value_objects.push_notification_value_object import PushNotificationValueObject
from src.user.models import User


@require_GET
def api_web_push_keys(request: HttpRequest) -> JsonResponse:
    return JsonResponse({
        'public_key': settings.WEB_PUSH_PUBLIC_KEY
    })


@require_GET
def test_notifications(request: HttpRequest) -> JsonResponse:
    only = request.GET.get('only')
    for_user = request.GET.get('for_user')
    notifications = []

    user = None
    if for_user:
        user = User.objects.get(username=for_user)

    if only == 'push' and user is not None:
        notifications.append(PushNotificationValueObject(
            body=f'This is test push notification {random.randint(1, 100000)}',
            title='Some cool title'
        ))
    elif only == 'email':
        notifications.append(EmailValueObject(
            subject='Test Email',
            template_path='emails/test_email.html',
            template_variables={'anchor_href': 'www.test.com', 'anchor_label': 'Click here to confirm your new email'},
            to=['admins']
        ))
    else:
        notifications.append(EmailValueObject(
            subject='Test Email',
            template_path='emails/test_email.html',
            template_variables={'anchor_href': 'www.test.com', 'anchor_label': 'Click here to confirm your new email'},
            to=['admins']
        ))

        notifications.append(PushNotificationValueObject(
            body=f'This is test push notification {random.randint(1, 100000)}. {settings.APP_URL}',
            title='Some cool title'
        ))

    bugsnag.notify(Exception(f'This is test error {random.randint(1, 100000)}'))
    NotificationService.send_notification(*notifications)

    return JsonResponse({'success': 'ok'})
