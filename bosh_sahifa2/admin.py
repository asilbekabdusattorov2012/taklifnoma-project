from django.contrib import admin
from .models import Invitation, BotUser, BotMessage

admin.site.register(Invitation)
admin.site.register(BotUser)
admin.site.register(BotMessage)
