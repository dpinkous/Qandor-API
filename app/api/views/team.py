from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.serializers.team import TeamSerializer, CreateTeamSerializer, UserSerializer, AddTeamMemberSerializer
from teams.models import Team


class MultiSerializerViewSet(viewsets.ModelViewSet):
    serializers = {
        'default': None
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers.get('default', None))


class TeamViewSet(MultiSerializerViewSet):
    """
    get:
    Get team of current logged user.
    put:
    Pass user id to add it to the team which current logged user is in.
    post:
    Create team with users by their username
    """
    permission_classes = (IsAuthenticated,)
    queryset = Team.objects.all()

    def get_object(self):
        try:
            team_id = self.request.user.team.id
        except AttributeError:
            raise Http404
        qs = self.get_queryset()
        return get_object_or_404(qs, id=team_id)

    serializers = {
        'retrieve': TeamSerializer,
        'create': CreateTeamSerializer,
        'update': AddTeamMemberSerializer,
        # etc.
    }
