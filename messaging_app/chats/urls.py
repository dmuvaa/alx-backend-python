from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import SimpleRouter
from chats.views import ConversationViewSet, MessageViewSet

router = SimpleRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
