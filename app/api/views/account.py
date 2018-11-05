from django.contrib.auth.signals import user_logged_in
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
import logging

from api.serializers.account import UserSerializer, UserProfileSerializer, UserFilterSerializer, UpdateUserSerializer
from accounts.models import User, UserProfile
from api.views.utils import MultiSerializerViewSet

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

user_profile_queryset = UserProfile.objects.select_related(
    'user'
).prefetch_related(
    'skills',
)

logger = logging.getLogger(__name__)


class RegisterAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (AllowAny,)

    def post(self, request):
        logger.error('LOGGING ERROR')
        logger.warning('LOGGIN WARNING')
        logger.info('LOGGING INFO')
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(user.password)
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewModel(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def post(self, request):
        permission_classes = (AllowAny,)
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    try:
        username = request.data['username']
        password = request.data['password']

        user = User.objects.get(username=username)
        if user.check_password(password):
            try:
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                user_details = {}
                user_details['token'] = token
                user_details['userID'] = '{}'.format(user.id)
                user_logged_in.send(sender=user.__class__,
                                    request=request, user=user)
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            res = {
                'error': 'Can not authenticate with the given credentials. The account might have been deactivated.'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        res = {
            'error': 'Can not authenticate with the given credentials. The account might have been deactivated.'}
        return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'Please provide a username and a password.'}
        return Response(res, status=status.HTTP_403_FORBIDDEN)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Returns user profile.

    update:
    Update user profile.
    """
    queryset = user_profile_queryset
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in self.kwargs:
            user_id = self.kwargs[lookup_url_kwarg]
        else:
            user_id = self.request.user.id

        qs = self.get_queryset()
        return get_object_or_404(qs, user_id=user_id)


class UserFilterBackend(DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        data = request.query_params.copy()
        if data['position'] == '':
            queryset = User.objects.filter(team__isnull=True, position__isnull=True)
        return {
            'data': data,
            'queryset': queryset,
            'request': request,
        }


class UserFilterViewSet(viewsets.ModelViewSet):
    """
    Return users matching filters: position, user_type and without team.
    """
    queryset = User.objects.all().filter(team__isnull=True)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserFilterSerializer
    filter_backends = (UserFilterBackend,)
    filter_fields = ('user_type', 'position')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.exclude(id=self.request.user.id)
        return queryset


class UserViewSet(MultiSerializerViewSet):
    """
    retrieve:
    Return current user
    update:
    Update current user
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), id=self.request.user.id)

    serializers = {
        'retrieve': UserSerializer,
        'update': UpdateUserSerializer
    }
