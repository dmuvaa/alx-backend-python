# messaging_app/chats/urls.py

from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter  # <-- ensures "NestedDefaultRouter" appears
from .views import ConversationViewSet, MessageViewSet

# Top-level router
router = routers.DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")

# Nested router: /api/conversations/{conversation_pk}/messages/
convo_router = NestedDefaultRouter(router, r"conversations", lookup="conversation")
convo_router.register(r"messages", MessageViewSet, basename="conversation-messages")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(convo_router.urls)),
]
