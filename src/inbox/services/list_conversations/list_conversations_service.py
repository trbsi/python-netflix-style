from http.cookiejar import cut_port_re

from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy

from src.core.utils import format_datetime
from src.inbox.models import Conversation
from src.user.models import User


class ListConversationsService():
    PER_PAGE = 25
    LAST_MESSAGE_SIZE = 50

    def list_conversations(self, current_user: User, current_page: int) -> dict:
        conversations = (
            Conversation.objects
            .filter(
                Q(sender=current_user, deleted_by_sender=False)
                | Q(recipient=current_user, deleted_by_recipient=False)
            )
            .select_related('sender', 'recipient')
            .order_by('-updated_at')
        )
        paginator = Paginator(object_list=conversations, per_page=self.PER_PAGE)
        page = paginator.page(current_page)

        result = []
        for conversation in page.object_list:
            other_user = conversation.get_other_user(current_user=current_user)
            message = conversation.last_message
            if message and len(message) > self.LAST_MESSAGE_SIZE:
                message = message[:self.LAST_MESSAGE_SIZE] + '...'

            result.append(
                {
                    'id': conversation.id,
                    'profile_picture': other_user.get_profile_picture(),
                    'username': other_user.username,
                    'updated_at': format_datetime(conversation.updated_at),
                    'last_message': message,
                    'is_read': conversation.is_read(current_user=current_user),
                    'messages_url': reverse_lazy('inbox.messages', kwargs={'conversation_id': conversation.id}),
                }
            )

        next_page = page.next_page_number() if page.has_next() else None

        return {'result': result, 'next_page': next_page}
