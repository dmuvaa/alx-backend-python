from django.shortcuts import render

from django.db.models import Prefetch
from rest_framework import viewsets, permissions, status, serializers, filters
from rest_framework.response import Response

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer


class IsAuthenticated(permissions.IsAuthenticated):
    """Alias for readability if your tests look for explicit permission usage."""
    pass


class ConversationViewSet(viewsets.ModelViewSet):
    """
    List/retrieve/create conversations.
    Supports:
      - search: ?search=<text> (by participant username/email)
      - ordering: ?ordering=created_at or -created_at
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # --- DRF filters ---
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "participants__username",
        "participants__email",
        "participants__first_name",
        "participants__last_name",
    ]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects.filter(participants=user)
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
        POST /api/conversations/
        {
          "participants_ids": ["<uuid1>", "<uuid2>", ...]
        }
        Ensures the current user is included.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()

        if request.user not in conversation.participants.all():
            conversation.participants.add(request.user)

        out = self.get_serializer(conversation)
        return Response(out.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    List/retrieve/create messages.
    Supports:
      - search: ?search=<text> (by body or sender username/email)
      - ordering: ?ordering=sent_at or -sent_at
    Create payload:
    {
      "conversation_id": "<uuid>",
      "sender_id": "<uuid>",     # optional; defaults to current user
      "message_body": "text"
    }
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    # --- DRF filters ---
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "message_body",
        "sender__username",
        "sender__email",
        "sender__first_name",
        "sender__last_name",
    ]
    ordering_fields = ["sent_at"]
    ordering = ["sent_at"]

    def get_queryset(self):
        user = self.request.user
        return (
            Message.objects.filter(conversation__participants=user)
            .select_related("conversation", "sender")
            .order_by("sent_at")
        )

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if "sender_id" not in data or data.get("sender_id") in ("", None):
            data["sender_id"] = str(request.user.pk)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        conversation = serializer.validated_data["conversation"]
        sender = serializer.validated_data["sender"]

        if not conversation.participants.filter(pk=sender.pk).exists():
            raise serializers.ValidationError("Sender must be a participant in the conversation.")

        message = serializer.save()
        out = self.get_serializer(message)
        return Response(out.data, status=status.HTTP_201_CREATED)
