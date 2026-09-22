import json
import logging
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bosh_sahifa.settings")
django.setup()

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from asgiref.sync import sync_to_async

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from bosh_sahifa2.models import BotUser, BotMessage


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
ADMIN_ID = settings.TELEGRAM_ADMIN_ID
ADMIN_USERNAME = getattr(settings, "TELEGRAM_ADMIN_USERNAME", "")
SITE_URL = settings.SITE_URL


if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN sozlanmagan.")


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()


# =========================
# ASOSIY MENYU
# =========================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌐 Saytga o'tish")],
        [KeyboardButton(text="👤 Men haqimda")],
        [KeyboardButton(text="💬 Bog'lanish")],
    ],
    resize_keyboard=True,
)


site_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🌐 Taklifnoma saytini ochish",
                url=SITE_URL,
            )
        ]
    ]
)


# =========================
# DATABASE
# =========================

@sync_to_async
def save_user(user):
    if not user:
        return False

    _, created = BotUser.objects.update_or_create(
        telegram_id=user.id,
        defaults={
            "username": user.username or "",
            "first_name": user.first_name or "",
        },
    )

    return created


@sync_to_async
def user_count():
    return BotUser.objects.count()


@sync_to_async
def remember_message(chat_id, message_id):
    BotMessage.objects.create(
        chat_id=chat_id,
        message_id=message_id,
    )


async def answer_and_remember(message: Message, text: str, **kwargs):
    sent = await message.answer(text, **kwargs)

    await remember_message(
        sent.chat.id,
        sent.message_id,
    )

    return sent


@sync_to_async
def get_all_saved_messages():
    return list(
        BotMessage.objects.values_list(
            "chat_id",
            "message_id",
        )
    )


@sync_to_async
def delete_all_saved_message_records():
    BotMessage.objects.all().delete()


# =========================
# START
# =========================

@dp.message(Command("start"))
async def start_handler(message: Message):

    is_new = await save_user(message.from_user)

    count = await user_count()

    await notify_admin_about_new_user(
        message,
        is_new,
    )

    name = (
        message.from_user.first_name or "mehmon"
    ).strip()

    username_note = ""

    if not message.from_user.username:
        username_note = (
            "\n\n⚠️ <b>Eslatma:</b> "
            "buyurtma berishda Telegram username kerak bo‘ladi. "
            "Telegram sozlamalaridan username o‘rnating."
        )

    await answer_and_remember(
        message,

        f"💌 <b>Taklifnoma</b>  •  "
        f"👤 <b>User: {count} ta</b>\n\n"

        f"Assalomu alaykum, "
        f"<b>{name}</b>! 👋\n\n"

        "Chiroyli taklifnoma shablonlarini ko‘ring "
        "va sayt orqali buyurtma bering. 😊"

        f"{username_note}\n\n"

        "👇 Kerakli bo‘limni tanlang:",

        reply_markup=main_keyboard,
    )


# =========================
# HELP
# =========================

@dp.message(Command("help"))
async def help_handler(message: Message):

    await save_user(message.from_user)

    await answer_and_remember(
        message,

        "ℹ️ <b>Yordam</b>\n\n"
        "🌐 Sayt orqali shablon tanlang va buyurtma bering.\n"
        "📱 Buyurtma uchun Telegram username kerak.\n"
        "💬 Savolingiz bo‘lsa, Bog'lanish bo‘limidan foydalaning.\n\n"
        "/start — asosiy menyu"
    )


# =========================
# ADMIN YANGI USER
# =========================

async def notify_admin_about_new_user(
    message: Message,
    is_new: bool,
):

    if not is_new or not ADMIN_ID:
        return

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "username yo‘q"
    )

    count = await user_count()

    text = (
        "👤 <b>YANGI FOYDALANUVCHI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"

        f"🧑 Ism: "
        f"{message.from_user.first_name or '—'}\n"

        f"🔗 Username: {username}\n"

        f"🆔 ID: "
        f"<code>{message.from_user.id}</code>\n"

        f"👥 Jami foydalanuvchilar: "
        f"<b>{count} ta</b>\n"

        f"👑 Admin: "
        f"{ADMIN_USERNAME or 'bot egasi'}"
    )

    try:

        await message.bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
        )

    except Exception as exc:

        logger.warning(
            "Admin xabari yuborilmadi: %s",
            exc,
        )


# =========================
# CLEAR
# =========================

@dp.message(Command("clear"))
async def clear_handler(message: Message):

    if (
        not ADMIN_ID
        or str(message.from_user.id) != str(ADMIN_ID)
    ):

        await answer_and_remember(
            message,
            "⛔ Bu buyruq faqat bot egasi uchun.",
        )

        return

    saved_messages = await get_all_saved_messages()

    deleted_count = 0

    for chat_id, message_id in saved_messages:

        try:

            await message.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )

            deleted_count += 1

        except Exception as e:

            logger.warning(
                "Xabarni o‘chirib bo‘lmadi: %s",
                e,
            )

    await delete_all_saved_message_records()

    await message.answer(
        f"✅ Botning saqlangan eski xabarlari "
        f"o‘chirildi. ({deleted_count} ta)",

        reply_markup=main_keyboard,
    )


# =========================
# SAYT
# =========================

@dp.message(F.text == "🌐 Saytga o'tish")
async def website_handler(message: Message):

    await save_user(message.from_user)

    await answer_and_remember(
        message,

        "🌐 <b>Taklifnoma sayti</b>\n\n"
        "Quyidagi tugmani bosing:",

        reply_markup=site_keyboard,
    )


# =========================
# MEN HAQIMDA
# =========================

@dp.message(F.text == "👤 Men haqimda")
async def about_handler(message: Message):

    await save_user(message.from_user)

    count = await user_count()

    text = f"""👨‍💻 <b>Men haqimda</b>

Mening ismim Asilbek. Men dasturiy ta’minot yaratish bilan shug‘ullanaman va IT sohasida o‘z bilim va ko‘nikmalarimni rivojlantirib kelmoqdaman. Dasturlash bo‘yicha faoliyatimni 2024-yildan boshlaganman.

Asosiy yo‘nalishim — foydalanuvchilar uchun qulay va zamonaviy dasturlar yaratish.

Hozirgi asosiy maqsadim — IT sohasi bo‘yicha sertifikat olish va kelajakda kiberxavfsizlik yo‘nalishida professional faoliyat yuritish.

Men yangi bilimlarni o‘rganishga va o‘z ustimda ishlashga intilaman.

👤 <b>Bot foydalanuvchilari: {count} ta</b>"""

    await answer_and_remember(
        message,
        text,
    )


# =========================
# BOG‘LANISH
# =========================

@dp.message(F.text == "💬 Bog'lanish")
async def contact_handler(message: Message):

    await save_user(message.from_user)

    await answer_and_remember(
        message,

        f"💬 <b>Bog'lanish</b>\n\n"

        f"Savolingiz bo‘lsa, "
        f"👑 Admin: {ADMIN_USERNAME or 'bot egasi'} "
        f"shu havolaga yozishingiz mumkin 😊\n\n"

        "Buyurtma berish uchun avval "
        "🌐 <b>Saytga o'tish</b> tugmasini bosing."
    )


# =========================
# BOSHQA XABARLAR
# =========================

@dp.message()
async def fallback_handler(message: Message):

    await save_user(message.from_user)

    await answer_and_remember(
        message,

        "Tushunmadim 🙂\n"
        "Pastdagi menyudan kerakli bo‘limni tanlang.",

        reply_markup=main_keyboard,
    )


# ==================================================
# TELEGRAM WEBHOOK
# ==================================================

@csrf_exempt
async def telegram_webhook(request):

    if request.method != "POST":
        return HttpResponse("Telegram webhook ishlayapti.")

    try:

        data = json.loads(
            request.body.decode("utf-8")
        )

        update = Update.model_validate(data)

        await dp.feed_update(
            bot,
            update,
        )

        return HttpResponse("OK")

    except Exception as exc:

        logger.exception(
            "Telegram webhook xatosi: %s",
            exc,
        )

        return HttpResponse(
            "Webhook error",
            status=500,
        )