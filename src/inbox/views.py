import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET, require_POST

from src.inbox.services.create_conversation.create_conversation_service import CreateConversationService
from src.inbox.services.delete_conversation.delete_conversation_service import DeleteConversationService
from src.inbox.services.inbox_settings.inbox_settings_service import InboxSettingsService
from src.inbox.services.list_conversations.list_conversations_service import ListConversationsService
from src.inbox.services.list_messages.can_user_access_conversation_specification import \
    CanUserAccessConversationSpecification
from src.inbox.services.list_messages.list_messages_service import ListMessagesService
from src.inbox.services.list_messages.read_messages_service import ReadConversationService
from src.inbox.services.send_message.send_message_service import SendMessageService
from src.user.models import User


# --------------------------------- CONVERSATIONS -------------------------------
@require_GET
@login_required
def list_conversations(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    inbox_settings_service = InboxSettingsService()
    auto_reply_active = inbox_settings_service.is_auto_reply_active(user)

    return render(
        request,
        'inbox_conversations.html',
        {
            'auto_reply_active': auto_reply_active,
            'is_creator': user.is_creator(),
            'list_conversations_api': reverse_lazy('inbox.api.list_conversations'),
            'delete_conversation_api': reverse_lazy('inbox.api.delete'),
            'toggle_auto_reply_api': reverse_lazy('inbox.api.toggle_auto_reply'),
        }
    )


@require_GET
@login_required
def create_conversations(request: HttpRequest, username: str) -> HttpResponse:
    service = CreateConversationService()
    id = service.get_or_create_conversation(sender=request.user, username=username)
    return redirect(reverse_lazy('inbox.messages', kwargs={'conversation_id': id}))


@require_GET
@login_required
def api_list_conversations(request: HttpRequest) -> JsonResponse:
    get = request.GET
    service = ListConversationsService()
    data = service.list_conversations(current_user=request.user, current_page=get.get('page'))

    return JsonResponse({'results': data['result'], 'next_page': data['next_page']})


@require_POST
@login_required
def api_delete(request: HttpRequest) -> JsonResponse:
    post = json.loads(request.body)
    service = DeleteConversationService()
    service.delete_conversations(ids=post['conversation_ids'], current_user=request.user)
    return JsonResponse({})


# --------------------------------- MESSAGES -------------------------------
@require_GET
@login_required
def list_messages(request: HttpRequest, conversation_id: int) -> HttpResponse:
    user = request.user
    specification = CanUserAccessConversationSpecification()
    result = specification.check(conversation_id=conversation_id, user=user)
    if not result:
        raise Http404

    read_service = ReadConversationService()
    conversation = read_service.read_conversation(conversation_id=conversation_id, user=user)
    other_user = conversation.get_other_user(current_user=user)

    return render(
        request,
        'inbox_messages.html',
        {
            'other_user': other_user,
            'current_user_id': user.id,
            'conversation_id': conversation_id,
            'list_messages_api': reverse_lazy(
                'inbox.api.list_messages',
                kwargs={'conversation_id': '__CONVERSATION_ID__'}
            ),
            'send_message_api': reverse_lazy('inbox.api.send_message'),
        }
    )


@require_GET
@login_required
def api_list_messages(request: HttpRequest, conversation_id: int) -> JsonResponse:
    get = request.GET
    after_id = int(get.get('after_id')) if get.get('after_id') is not None else None
    page = int(get.get('page')) if get.get('page') is not None else 1
    user = request.user

    specification = CanUserAccessConversationSpecification()
    result = specification.check(conversation_id=conversation_id, user=user)
    if not result:
        raise Http404

    service = ListMessagesService()
    result = service.list_messages(conversation_id=conversation_id, current_page=page, after_id=after_id)

    return JsonResponse({'results': result['result'], 'next_page': result['next_page']})


@require_POST
@login_required
def api_send_message(request: HttpRequest) -> JsonResponse:
    post = request.POST
    files = request.FILES

    service = SendMessageService()
    message = service.send_message(
        user=request.user,
        message_content=post.get('message'),
        conversation_id=int(post.get('conversationId')),
        uploaded_file=files.get('attachment')
    )

    return JsonResponse(message)


@require_POST
@login_required
def api_toggle_auto_reply(request: HttpRequest) -> JsonResponse:
    user: User | AnonymousUser = request.user
    if user.is_anonymous or user.is_regular_user():
        return JsonResponse({})

    body = json.loads(request.body)
    auto_reply_active = bool(body.get('auto_reply_active'))
    service = InboxSettingsService()
    settings = service.update_settings(user=user, auto_reply_active=auto_reply_active)

    return JsonResponse({'auto_reply_active': settings.auto_reply_active})
