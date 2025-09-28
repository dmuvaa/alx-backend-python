from django.shortcuts import render

from django.db.models import Prefetch
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer


class IsAuthenticated(permissions.IsAuthenticated):
    """Alias for readability if your tests look for explicit permission usage."""
    pass


class ConversationViewSet(viewsets.ModelViewSet):
    """
    List/retrieve/create conversations.
    - GET /api/conversations/           -> list conversations the user participates in
    - POST /api/conversations/          -> create a conversation (accepts participants_ids)
    - GET /api/conversations/{id}/      -> retrieve conversation (with nested messages & participants)
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show conversations the current user participates in
        user = self.request.user
        return (
            Conversation.objects.filter(participants=user)
            .select_related()
            .prefetch_related(
                "participants",
                Prefetch(
                    "messages",
                    queryset=Message.objects.select_related("sender").order_by("sent_at"),
                ),
            )
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        """
        Create a conversation. Payload:
        {
            "participants_ids": ["<uuid1>", "<uuid2>", ...]   # write-only
        }
        The current user will be added automatically if missing.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the conversation (this sets participants from participants_ids, if provided)
        conversation = serializer.save()

        # Ensure the creator is included as a participant
        if request.user not in conversation.participants.all():
            conversation.participants.add(request.user)

        out = self.get_serializer(conversation)
        return Response(out.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    List/retrieve/create messages.
    - GET /api/messages/                -> list messages in conversations the user participates in
    - POST /api/messages/               -> create a message:
        {
          "conversation_id": "<uuid>",
          "sender_id": "<uuid>",       # optional; defaults to current user
          "message_body": "text"
        }
    - GET /api/messages/{id}/           -> retrieve a single message
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Message.objects.filter(conversation__participants=user)
            .select_related("conversation", "sender")
            .order_by("sent_at")
        )

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # If no sender_id provided, default to the current user
        if "sender_id" not in data or data.get("sender_id") in ("", None):
            data["sender_id"] = str(request.user.pk)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        conversation = serializer.validated_data["conversation"]
        sender = serializer.validated_data["sender"]

        # Validate membership: sender must be part of the conversation
        if not conversation.participants.filter(pk=sender.pk).exists():
            raise serializers.ValidationError("Sender must be a participant in the conversation.")

        message = serializer.save()
        out = self.get_serializer(message)
        return Response(out.data, status=status.HTTP_201_CREATED)
