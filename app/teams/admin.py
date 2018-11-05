from django.contrib import admin

from accounts.models import User
from .models import Team

admin.site.register(Team)

