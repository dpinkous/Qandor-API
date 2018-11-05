from django.core import serializers
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Max

from conversations.models import Conversation, Message
from api.serializers.conversation import ConversationSerializer, CreateMessageSerializer, MessageSerializer, \
    ConversationDetailsSerializer, CreateConversationSerializer, MarkAsReadConversationSerializer
from conversations.filters import MessageFilter

conversations_queryset = Conversation.objects.prefetch_related(
    'users',
    'messages',
)


class MessagePagination(CursorPagination):
    page_size = 7
    page_size_query_param = 'page_size'
    ordering = '-position'


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = (IsAuthenticated,)
    queryset = conversations_queryset

    def create(self, request, *args, **kwargs):
        """
        Create a conversation, with logged in user added to the userlist
        """
        data = request.data.copy()
        serializer = CreateConversationSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            instance = serializer.save()
            context = {
                'user': request.user
            }
            data = ConversationSerializer(instance, context=context)
            return Response(data.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
        Get a list of all conversations that the logged user is in
        """
        queryset = self.get_queryset()
        conversations_list = get_list_or_404(
            queryset.annotate(last_updated=Max("messages__created_at")).order_by("-last_updated"), users__id=request.user.id)
        context = {
            'user': request.user
        }
        serializer = ConversationSerializer(conversations_list, context=context, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Input - conversation id. Get a detailed view of a conversation if the logged user is in it.
        """
        message_id = request.GET.get('id')
        queryset = Conversation.objects.filter(users__id=request.user.id)
        conversation = get_object_or_404(queryset, pk=pk)
        context = {
            'request': request,
            'message_position': None
        }
        if message_id:
            message = Message.objects.get(id=message_id)
            context['message_position'] = message.position - \
                                          3 if message.position > 3 else 0
        serializer = ConversationDetailsSerializer(
            conversation, context=context)
        return Response(serializer.data)

    @action(methods=['put'], detail=False)
    def mark_read(self, request):
        """
        Input - message id. Adds logged user to a list of users that read the message.
        """
        conversation_id = request.GET.get('id', '')
        if conversation_id:
            conversation = Conversation.objects.get(id=conversation_id)
            data = request.data.copy()
            data['read_by'] = request.user
            serializer = MarkAsReadConversationSerializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)
            except serializers.ValidationError:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.update(conversation, data)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def message(self, request, pk=None):
        """
        Input - text, image(optional), mobile_uid. Adds a new message to the conversation.
        """
        queryset = Conversation.objects.filter(users__id=request.user.id)
        conversation = get_object_or_404(queryset, pk=pk)
        data = request.data.copy()
        if conversation.messages.last():
            message_position = conversation.messages.last().position + 1
        else:
            message_position = 0
        data['position'] = message_position
        data['user'] = request.user.id
        data['conversation'] = conversation.id
        data['sent'] = True
        serializer = CreateMessageSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def serach(self, request):
        """
        Input - searched phrase. Shows a list of conversations where the
         searched phrase exists in one of the messages, only shows conversations the user is in.
        """
        filterset_class = MessageFilter
        return filterset_class


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = MessageFilter

    def get_queryset(self):
        user = self.request.user
        qs = Message.objects.filter(conversation__users=user)
        return qs
