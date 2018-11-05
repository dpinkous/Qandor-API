from django.db import models
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers



from api.serializers.account import UserNestedSerializer
from api.serializers.team import TeamSerializer
from conversations.models import Conversation, Message


class CreateMessageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)

    class Meta:
        model = Message
        fields = ('id', 'text', 'created_at', 'user', 'image', 'conversation', 'position', 'mobile_uid')


class MessageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)
    user = UserNestedSerializer()

    class Meta:
        model = Message
        fields = ('id', 'text', 'created_at', 'user', 'image', 'conversation', 'position', 'mobile_uid')


class ConversationSerializer(serializers.ModelSerializer):
    users = UserNestedSerializer(many=True, read_only=True)
    team = TeamSerializer(read_only=True)
    last_message_text = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    read = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'users', 'last_message_text', 'last_message_time', 'team', 'read')

    def get_last_message_text(self, obj):
        try:
            msg = obj.messages.last()
        except AttributeError:
            msg = None
        return msg.text if msg else None

    def get_last_message_time(self, obj):
        try:
            msg = obj.messages.last()
        except AttributeError:
            msg = None
        return msg.created_at if msg else None

    def get_read(self, obj):
        user = self.context['user']
        qs = obj.messages.filter(~models.Q(read_by=user))
        return False if qs else True


class CreateConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = ('id', 'users')


class ConversationDetailsSerializer(serializers.ModelSerializer):
    users = UserNestedSerializer(many=True)
    messages = serializers.SerializerMethodField()
    read = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'users', 'messages', 'read')

    def get_messages(self, obj):
        if self.context['message_position']:
            qs = obj.messages.filter(position__gte=self.context['message_position'])
        else:
            qs = obj.messages.all()
        return MessageSerializer(qs, many=True, read_only=True).data

    def get_read(self, obj):
        user = self.context['request'].user
        qs = obj.messages.filter(~models.Q(read_by=user))
        return False if qs else True


class MarkAsReadConversationSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        added = validated_data.get('read_by', None)
        if added:
            for message in instance.messages.all():
                message.read_by.add(added)

    class Meta:
        model = Conversation
        fields = ('id', )
