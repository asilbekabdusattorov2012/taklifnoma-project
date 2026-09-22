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
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from aiogram.types import Update

from .telegram_bot import bot, dp


@csrf_exempt
async def telegram_webhook(request):

    if request.method != "POST":
        return HttpResponse("Telegram webhook ishlayapti.")

    try:
        data = json.loads(request.body.decode("utf-8"))

        update = Update.model_validate(data)

        await dp.feed_update(
            bot,
            update,
        )

        return HttpResponse("OK")

    except Exception as exc:
        return HttpResponse(
            f"Webhook error: {exc}",
            status=500,
        )