from django.contrib import admin

from .models import Event
from .models import TeamMessage
from .models import UserProfile

admin.site.register(Event)
admin.site.register(TeamMessage)
admin.site.register(UserProfile)
