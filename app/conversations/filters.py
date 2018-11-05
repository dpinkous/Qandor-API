import rest_framework_filters as filters

from .models import Conversation, Message


class MessageFilter(filters.FilterSet):
    text = filters.CharFilter(label="text", method="message_filter")

    class Meta:
        model = Message
        fields = []

    def message_filter(self, queryset, text, value):
        user = self.request.user
        return queryset.filter(**{
            'conversation__users': user,
            'text__icontains': value
        }).distinct()
