from pathlib import Path

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET

from automationapp import settings
from src.notification.services.notification_service import NotificationService
from src.notification.value_objects.email_value_object import EmailValueObject
from src.notification.value_objects.push_notification_value_object import PushNotificationValueObject


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'home.html',
        {'feed_api_url': reverse_lazy('media.api.get_media')}
    )


@require_GET
def legal_documents(request: HttpRequest) -> HttpResponse:
    document = request.GET.get('document')
    dir = Path(f'{settings.BASE_DIR}/static/legal_documents')
    files = []
    for file in dir.iterdir():
        if not file.is_file() or file.suffix != '.pdf':
            continue

        if document and document.lower() in file.name.lower():
            return redirect(f'/static/legal_documents/{file.name}')

        file_name = (
            file.name
            .replace('_', ' ')
            .replace('-', ' ')
            .replace('.pdf', '')
            .title())
        files.append({'file': file.name, 'name': file_name})

    return render(request, 'legal_documents.html', {'legal_documents': files})


@require_GET
def terms_of_use(request: HttpRequest) -> HttpResponse:
    return render(request, 'terms_of_use.html')


@require_GET
def privacy_policy(request: HttpRequest) -> HttpResponse:
    return render(request, 'privacy_policy.html')


@require_GET
def landing_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'landing_page.html')


def contact(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        post = request.POST
        NotificationService.send_notification(
            EmailValueObject(
                subject='Support',
                template_path='emails/core/contact.html',
                template_variables={'body': post.get('message'), 'name': post.get('name')},
                to=['admins'],
                reply_to_email=post.get('email'),
                reply_to_name=post.get('name'),
            ),
            PushNotificationValueObject(body='Check your email, there is new support email sent by someone')
        )
        messages.success(request, 'We will get back to you soon!')
    return render(request, 'contact.html', {'company': settings.APP_NAME})
