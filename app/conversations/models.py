from datetime import datetime
from django.db import models
import os
import uuid

from accounts.models import User
from teams.models import Team


def path_name(instance, filename):
    extension = os.path.splitext(filename)[1]
    return os.path.join('conversations', f'conversation_{instance.conversation.id}', f'{str(uuid.uuid4())}{extension}')


class Conversation(models.Model):

    users = models.ManyToManyField(User, blank=True)
    team = models.OneToOneField(Team, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        default_related_name = "conversations"


class Message(models.Model):

    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, default=None)
    image = models.ImageField(upload_to=path_name, blank=True, null=True)
    position = models.PositiveIntegerField()
    mobile_uid = models.CharField(max_length=64)
    sent = models.BooleanField(default=False)
    recieved = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name="readby", blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.text

    class Meta:
        default_related_name = "messages"
        unique_together = ('position', 'conversation')
        ordering = ('created_at', 'position')
