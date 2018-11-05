from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from accounts.models import User, UserProfile, Skill


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)
    date_joined = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'user_type',
                  'date_joined', 'position', 'password', 'image', 'company', 'phone_number')
        extra_kwargs = {'password': {'write_only': True}}


class UserNestedSerializer(DynamicFieldsModelSerializer):
    image = Base64ImageField(required=False)
    full_name = serializers.CharField(source='get_full_name')

    class Meta(object):
        model = User
        fields = ('id', 'username', 'full_name', 'image', 'phone_number')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    skills = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='user.get_full_name')
    position = serializers.CharField(source='user.position')

    def get_skills(self, profile):
        return [skill.name for skill in profile.skills.all()]

    class Meta(object):
        model = UserProfile
        fields = ('id', 'user', 'full_name', 'number_of_votes', 'score', 'skills', 'description', 'position')


class UserFilterSerializer(serializers.ModelSerializer):
    # company = serializers.CharField(source='profile.company')

    class Meta(object):
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'user_type', 'image', 'position')


class UpdateUserSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)

    class Meta(object):
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'position', 'image', 'phone_number')
