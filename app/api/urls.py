from django.conf import settings
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from api.views.account import RegisterAPIView, authenticate_user, UserProfileViewSet, UserFilterViewSet, UserViewSet
from api.views.conversation import ConversationViewSet, MessageViewSet
from api.views.team import TeamViewSet

user = UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update'
})

users = UserFilterViewSet.as_view({
    'get': 'list'
})

user_profile = UserProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update'
})

user_profile_detail = UserProfileViewSet.as_view({
    'get': 'retrieve'
})

conversation_list = ConversationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
conversation_details = ConversationViewSet.as_view({
    'get': 'retrieve'
})
send_message = ConversationViewSet.as_view({
    'post': 'message'
})
mark_as_read = ConversationViewSet.as_view({
    'put': 'mark_read'
})
filter_messages = MessageViewSet.as_view({
    'get': 'list'
})


team = TeamViewSet.as_view({
    'get': 'retrieve',
    'post': 'create'
})

add_team_member = TeamViewSet.as_view({
    'put': 'update'
})

urlpatterns = format_suffix_patterns([
    url(r'^accounts/create/$', RegisterAPIView.as_view()),
    url(r'^accounts/user/$', user),
    url(r'^accounts/profile/$', user_profile),
    url(r'^accounts/profile/(?P<pk>[0-9]+)/$', user_profile_detail),
    url(r'^accounts/users/$', users),
    url(r'^accounts/login/$', authenticate_user),
    url(r'^conversations/$', conversation_list, name='conversation-list'),
    url(r'^conversations/search/$', filter_messages, name='filter-messages'),
    url(r'^conversations/markread/$', mark_as_read, name='mark-as-read'),
    url(r'^conversations/(?P<pk>[0-9]+)/$', conversation_details, name='conversation-detail'),
    url(r'^conversations/(?P<pk>[0-9]+)/message/$', send_message, name='send-message'),
    url(r'^team/$', team),
    url(r'^team/add-member/$', add_team_member, name='add-team-member'),

])
