# messaging_app/chats/serializers.py

from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
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
    # Read: show sender details; Write: accept sender_id & conversation_id
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="sender", queryset=User.objects.all()
    )
    conversation_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="conversation", queryset=Conversation.objects.all()
    )
    # Optional: expose conversation UUID on read (without expanding)
    conversation = serializers.UUIDField(
        source="conversation.conversation_id", read_only=True
    )

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


class ConversationSerializer(serializers.ModelSerializer):
    # Read: nested participants + nested messages
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    # Write: accept list of participant UUIDs
    participants_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        source="participants",
        queryset=User.objects.all(),
    )

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participants_ids",  # write-only
            "messages",
            "created_at",
        ]
        read_only_fields = ["conversation_id", "created_at", "participants", "messages"]

    def create(self, validated_data):
        """
        Allow creating a conversation with participants:
        {
          "participants_ids": ["<uuid1>", "<uuid2>", ...]
        }
        """
        participants = validated_data.pop("participants", [])
        conversation = Conversation.objects.create(**validated_data)
        if participants:
            conversation.participants.set(participants)  # through model auto-created
        return conversation

    def update(self, instance, validated_data):
        """
        Optionally update the participant list.
        """
        participants = validated_data.pop("participants", None)
        instance = super().update(instance, validated_data)
        if participants is not None:
            instance.participants.set(participants)
        return instance
