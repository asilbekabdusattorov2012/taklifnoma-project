from django.shortcuts import render
from .models import Invitation


def invitations_list(request):
    invitations = Invitation.objects.all().order_by("-created_at")

    return render(
        request,
        "invitations_list.html",
        {
            "invitations": invitations
        }
    )