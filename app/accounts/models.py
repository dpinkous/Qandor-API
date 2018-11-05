from django.core.mail import send_mail
from django.db import models, transaction
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, UserManager
)
from drf_extra_fields.fields import Base64ImageField
from markdownx.models import MarkdownxField
import os
import uuid
from phonenumber_field.modelfields import PhoneNumberField

from teams.models import Team


def path_name(instance, filename):
    extension = os.path.splitext(filename)[1]
    return os.path.join('users', f'user_{instance.id}', f'{str(uuid.uuid4())}{extension}')


class MyUserManager(UserManager):

    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given email,and password.
        """
        if not username:
            raise ValueError('Username is required.')
        if not email:
            raise ValueError('Email is required.')
        if not password:
            raise ValueError('Password is required.')
        try:
            with transaction.atomic():
                user = self.model(username=username, email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except:
            raise

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    """
    POSITION_TYPE_FINANCIAL_ADVISOR = 'financial_advisor'
    POSITION_TYPE_INSURANCE_AGENT = 'insurance_agent'
    POSITION_TYPE_ATTORNEY = 'attorney'
    POSITION_TYPE_REAL_ESTATE_AGENT = 'real_estate_agent'
    POSITION_TYPE_TAX_PRO = 'tax_pro'
    POSITION_TYPE_MORTGAGE_PRO = 'mortgage_pro'

    USER_TYPE_STANDARD = 'standard'
    USER_TYPE_PRO = 'pro'

    POSITION_LIST = (
        (POSITION_TYPE_FINANCIAL_ADVISOR, 'Financial Advisor'),
        (POSITION_TYPE_INSURANCE_AGENT, 'Insurance Agent'),
        (POSITION_TYPE_ATTORNEY, 'Attorney'),
        (POSITION_TYPE_REAL_ESTATE_AGENT, 'Real Estate Agent'),
        (POSITION_TYPE_TAX_PRO, 'Tax Pro'),
        (POSITION_TYPE_MORTGAGE_PRO, 'Mortgage Pro'),
    )

    USER_TYPE_LIST = (
        (USER_TYPE_STANDARD, 'Standard user'),
        (USER_TYPE_PRO, 'Pro user')
    )

    username = models.CharField(max_length=40, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=60, unique=True)
    company = models.CharField(blank=True, max_length=50)
    position = models.CharField(choices=POSITION_LIST, blank=True, null=True, db_index=True, max_length=30)
    # phone_regex = RegexValidator(regex=r'/\(?([0-9]{3})\)?([ .-]?)([0-9]{3})\2([0-9]{4})/', message="Please, enter a valid phone number.")
    # phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    user_type = models.CharField(choices=USER_TYPE_LIST, default=USER_TYPE_STANDARD, max_length=40)
    image = models.ImageField(upload_to=path_name, default='users/default.png')
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return '{} {}'.format(self.username, self.get_full_name)

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self

    @property
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        default_related_name = 'users'


class Skill(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=60, blank=True, null=True)
    number_of_votes = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    skills = models.ManyToManyField(Skill, blank=True)
    description = MarkdownxField(blank=True, null=True)

    class Meta:
        default_related_name = 'profile'

    def __str__(self):
        return self.user.username
