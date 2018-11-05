from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from itertools import combinations

from .models import Team
from accounts.models import User
from api.serializers.conversation import ConversationSerializer


@receiver(pre_save, sender=Team)
def create_conversations(sender, instance, **kwargs):
    print('---------------------')
    print('you are in a receiver')
    print('---------------------')
    # if instance.pk:
    #     old_instance = Team.objects.get(pk=instance.pk)
    #     if not old_instance.users == instance.users:
    #         print('---------------------')
    #         print('userlist got modified')
    #         print('---------------------')
    #         users = [user for user in instance.users.all()]
    #         team_conversation = Conversation.objects.get(team__id=instance.id)
    #         if not team_conversation:
    #             print('---------------------')
    #             print('team conversation gets created')
    #             print('---------------------')
    #             new_conversation = Conversation.objects.create(
    #                 team=instance.id
    #             )
    #         for user in users:
    #             if user not in old_instance.users:
    #                 new_conversation.users.add()
    #         if len(users) > 2:
    #             print('---------------------')
    #             print('there are more than 3 users')
    #             print('---------------------')
    #             conversations_list = combinations(users, 2)
    #             for conversation in conversations_list:
    #                 print('---------------------')
    #                 print(f'trying to create a conversation for {conversation[0].id} and {conversation[1].id}')
    #                 print('---------------------')
    #                 existing_coversation = Conversation.objects.filter(team__id=None).filter(users__id=conversation[0].id).get(users__id=conversation[1].id)
    #                 print(existing_coversation)
    #                 if not existing_coversation:
    #                     print('---------------------')
    #                     print('conversation exists')
    #                     print('---------------------')
    #                     new_conversation = Conversation.objects.create()
    #                     new_conversation.users.add(*[user for user in conversation])
    #                     new_conversation.save()
    #         new_conversation.save()
