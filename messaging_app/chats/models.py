import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user with UUID PK, unique email, phone, role, and created_at.
    Uses AbstractUser to keep Django's auth features (username, password hashing, etc.).
    """
    class Role(models.TextChoices):
        GUEST = "guest", "Guest"
        HOST = "host", "Host"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    # Enforce unique, non-null email
    email = models.EmailField(unique=True)

    phone_number = models.CharField(max_length=32, blank=True, null=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GUEST)
    created_at = models.DateTimeField(auto_now_add=True)

    # Keep username-based auth (default). If you want email login later,
    # you can set USERNAME_FIELD = "email" and handle migrations accordingly.

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"


class Conversation(models.Model):
    """
    A conversation with 2+ participants (users).
    Track participants via a through table to avoid duplicates and enable metadata per membership.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    participants = models.ManyToManyField(
        "User",
        through="ConversationParticipant",
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Conversation {self.id}"


class ConversationParticipant(models.Model):
    """
    M2M through model so each (conversation, user) pair is unique.
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
    id = models.UUIDField(
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
        body_preview = (self.message_body[:30] + "…") if len(self.message_body) > 30 else self.message_body
        return f"{self.sender} -> {self.conversation_id}: {body_preview}"
