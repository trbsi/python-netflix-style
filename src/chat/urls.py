from django.urls import path

from src.chat import views

urlpatterns = [
    path('webhook', views.webhook, name='chat.webhook'),
    path('set-webhook', views.set_webhook),
    path('test-reply', views.test_reply, name='chat.test_reply'),
]
