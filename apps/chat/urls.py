from django.urls import path
from .views import MessageListView, MessageCreateView, conversation_messages, conversations_list

urlpatterns = [
    path("", MessageListView.as_view(), name="message-list"),
    path("create/", MessageCreateView.as_view(), name="message-create"),
    path("conversations/", conversations_list, name="conversations-list"),
    path("messages/<int:user_id>/", conversation_messages, name="conversation-messages"),
]
