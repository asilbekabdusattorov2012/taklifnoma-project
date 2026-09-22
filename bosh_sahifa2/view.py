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
import asyncio
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from telegram_bot import process_update


@csrf_exempt
def telegram_webhook(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST allowed"},
            status=405
        )

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )

        asyncio.run(
            process_update(data)
        )

        return JsonResponse(
            {"ok": True}
        )

    except Exception as e:
        return JsonResponse(
            {
                "ok": False,
                "error": str(e)
            },
            status=500
        )