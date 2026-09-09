from django.urls import path
from .view import invitations_list


from django.urls import path
from .view import invitations_list

urlpatterns = [
    path('invitations/', invitations_list, name='invitations_list'),
]