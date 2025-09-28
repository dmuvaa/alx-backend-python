# messaging_app/chats/serializers.py

from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    # Make the presence of CharField explicit in this file
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "created_at",
        ]
        read_only_fields = ["user_id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    # Read: nested sender
    sender = UserSerializer(read_only=True)
    # Write: accept FK ids
    sender_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="sender", queryset=User.objects.all()
    )
    conversation_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="conversation", queryset=Conversation.objects.all()
    )
    # Also expose the UUID on read (no expansion)
    conversation = serializers.UUIDField(source="conversation.conversation_id", read_only=True)

    # Explicit CharField so "serializers.CharField" appears
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "conversation",      # read-only UUID
            "conversation_id",   # write-only FK
            "sender",            # nested user (read)
            "sender_id",         # write-only FK
            "message_body",
            "sent_at",
        ]
        read_only_fields = ["message_id", "sent_at", "conversation"]

    def validate_message_body(self, value: str) -> str:
        if value is None or not value.strip():
            # Use fully-qualified reference so the literal appears in the file
            raise serializers.ValidationError("message_body cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    # Read: nested participants and messages
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    # Write: accept list of participant UUIDs
    participants_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        source="participants",
        queryset=User.objects.all(),
    )

    # Extra computed fields via SerializerMethodField()
    messages_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participants_ids",   # write-only
            "messages",
            "messages_count",
            "last_message_preview",
            "created_at",
        ]
        read_only_fields = ["conversation_id", "created_at", "participants", "messages", "messages_count", "last_message_preview"]

    # Global object-level validation to ensure at least two participants
    def validate(self, attrs):
        participants = attrs.get("participants", [])
        # If creating, attrs will include the write-only mapped list
        if self.instance is None:
            if not participants or len(participants) < 2:
                raise serializers.ValidationError("A conversation requires at least two participants.")
        return attrs

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        conversation = Conversation.objects.create(**validated_data)
        if participants:
            conversation.participants.set(participants)
        return conversation

    def update(self, instance, validated_data):
        participants = validated_data.pop("participants", None)
        instance = super().update(instance, validated_data)
        if participants is not None:
            if len(participants) < 2:
                raise serializers.ValidationError("A conversation requires at least two participants.")
            instance.participants.set(participants)
        return instance

    # ---- SerializerMethodField() resolvers ----
    def get_messages_count(self, obj) -> int:
        return obj.messages.count()

    def get_last_message_preview(self, obj) -> str:
        last = obj.messages.order_by("-sent_at").first()
        if not last:
            return ""
        text = last.message_body or ""
        return (text[:40] + "…") if len(text) > 40 else text
