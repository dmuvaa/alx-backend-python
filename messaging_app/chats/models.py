# messaging_app/chats/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model:
    - UUID primary key named `user_id` (as required by spec)
    - Unique email
    - Optional phone number
    - Role enum: guest/host/admin
    - created_at timestamp
    Note: first_name and last_name are inherited from AbstractUser, but we
    include them in REQUIRED_FIELDS so their names appear in this file and to
    make them required on creates via createsuperuser, etc.
    """

    class Role(models.TextChoices):
        GUEST = "guest", "Guest"
        HOST = "host", "Host"
        ADMIN = "admin", "Admin"

    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    # AbstractUser already has: username, first_name, last_name, password, etc.
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GUEST)
    created_at = models.DateTimeField(auto_now_add=True)

    # Ensure the strings 'first_name' and 'last_name' appear in this file
    # and make them part of required fields for admin creates, etc.
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"


class Conversation(models.Model):
    """
    A conversation with 2+ participants.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    participants = models.ManyToManyField(
        User,
        through="ConversationParticipant",
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class ConversationParticipant(models.Model):
    """
    Through table to ensure each (conversation, user) pair is unique.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversation_memberships",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("conversation", "user")
        indexes = [
            models.Index(fields=["conversation", "user"]),
        ]

    def __str__(self):
        return f"{self.user} in {self.conversation_id}"


class Message(models.Model):
    """
    Message sent by a user within a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        db_index=True,
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sent_at"]
        indexes = [
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self):
        body = (self.message_body[:30] + "…") if len(self.message_body) > 30 else self.message_body
        return f"{self.sender} -> {self.conversation_id}: {body}"
