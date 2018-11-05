from django.http import Http404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from accounts.models import User
from teams.models import Team
from conversations.models import Conversation


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')

    class Meta(object):
        model = User
        fields = ('id', 'username', 'full_name', 'user_type', 'position', 'image')


class TeamSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    name = serializers.CharField()

    class Meta(object):
        model = Team
        fields = ('id', 'name', 'users')

    def create(self, validated_data):
        ModelClass = self.Meta.model
        instance = ModelClass.objects.create(**validated_data)
        user = self.context['request'].user
        user.team = instance
        user.save()
        return instance


class AddTeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta(object):
        model = Team
        fields = ('user', 'user_id')

    def update(self, instance, validated_data):
        user_id = validated_data['user_id']
        request_user = self.context['request'].user
        try:
            new_user = User.objects.get(id=user_id)
            try:
                team_conversation = Conversation.objects.get(team__id=instance.id)
                team_conversation.users.add(new_user)
                team_conversation.save()
            except Conversation.DoesNotExist:
                team_conversation = Conversation.objects.create()
                team_conversation.users.add(request_user)
                team_conversation.users.add(new_user)
                team_conversation.save()
            for user in instance.users.all():
                try:
                    existing_coversation = Conversation.objects.filter(team__id=None).filter(users__id=new_user.id).get(
                        users__id=user.id)
                except Conversation.DoesNotExist:
                    new_conversation = Conversation.objects.create()
                    new_conversation.users.add(new_user)
                    new_conversation.users.add(user)
                    new_conversation.save()
            new_user.team = instance
            new_user.save()
            instance.user = new_user
            return instance
        except User.DoesNotExist:
            raise Http404


class CreateTeamSerializer(serializers.ModelSerializer):
    users = SlugRelatedField(many=True, queryset=User.objects.all().filter(team__isnull=True), slug_field='username')
    name = serializers.CharField()

    class Meta(object):
        model = Team
        fields = ('name', 'users')

    def create(self, validated_data):
        instance = Team.objects.create(name=validated_data['name'])
        user = self.context['request'].user
        for elem in validated_data['users']:
            if user == elem:
                continue
            instance.users.add(elem)
        instance.save()
        user.team = instance
        user.save()
        team_conversation = Conversation.objects.create()
        team_conversation.save()
        team_conversation.team = instance
        team_conversation.users.add(user)
        team_conversation.save()
        return instance
