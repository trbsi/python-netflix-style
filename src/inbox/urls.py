from django.urls import path

from . import views

urlpatterns = [
    path('conversations', views.list_conversations, name='inbox.conversations'),
    path('send-message/<str:username>', views.create_conversations, name='inbox.create_conversations'),
    path('conversations/<int:conversation_id>/messages', views.list_messages, name='inbox.messages'),

    path('api/delete', views.api_delete, name='inbox.api.delete'),
    path('api/list-conversations', views.api_list_conversations, name='inbox.api.list_conversations'),
    path('api/conversations/<conversation_id>/list-messages', views.api_list_messages, name='inbox.api.list_messages'),
    path('api/send-message', views.api_send_message, name='inbox.api.send_message'),
    path('api/toggle-auto-reply', views.api_toggle_auto_reply, name='inbox.api.toggle_auto_reply'),
]
