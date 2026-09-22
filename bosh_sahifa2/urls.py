from django.urls import path
from .view import invitations_list,telegram_webhook


urlpatterns = [
    path('invitations/', invitations_list, name='invitations_list'),
    path("telegram/webhook/", telegram_webhook, name="telegram_webhook"),
]