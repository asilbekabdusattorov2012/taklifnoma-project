import logging
import os

import django
from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bosh_sahifa.settings")
django.setup()

from django.conf import settings
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
)

from bosh_sahifa2.models import BotUser, BotMessage


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or getattr(
    settings, "TELEGRAM_BOT_TOKEN", ""
)

ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID") or getattr(
    settings, "TELEGRAM_ADMIN_ID", ""
)

ADMIN_USERNAME = os.getenv("TELEGRAM_ADMIN_USERNAME") or getattr(
    settings, "TELEGRAM_ADMIN_USERNAME", "asibek_abdusattorov"
)

SITE_URL = os.getenv("SITE_URL") or getattr(
    settings, "SITE_URL", ""
)


if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN sozlanmagan!")


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🌐 Saytga o'tish"),
            KeyboardButton(text="👤 Men haqimda"),
        ],
        [
            KeyboardButton(text="📊 Statistika"),
            KeyboardButton(text="💬 Bog'lanish"),
        ],
    ],
    resize_keyboard=True,
)


site_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🌐 Saytga o'tish",
                url=SITE_URL if SITE_URL else "https://google.com"
            )
        ]
    ]
)


@sync_to_async
def save_user(message: Message):
    user = message.from_user

    if not user:
        return None, False

    telegram_id = user.id

    obj, created = BotUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": user.username or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
        },
    )

    if not created:
        obj.username = user.username or ""
        obj.first_name = user.first_name or ""
        obj.last_name = user.last_name or ""
        obj.save()

    return obj, created


@sync_to_async
def get_user_count():
    return BotUser.objects.count()


@sync_to_async
def save_message(message: Message):
    user = message.from_user

    if not user:
        return

    BotMessage.objects.create(
        telegram_id=user.id,
        username=user.username or "",
        message=message.text or "",
    )


async def notify_admin(message: Message):
    if not ADMIN_ID:
        return

    user = message.from_user

    if not user:
        return

    text = (
        "🆕 <b>Yangi foydalanuvchi!</b>\n\n"
        f"👤 Ism: {user.first_name or '-'}\n"
        f"🔹 Username: @{user.username or '-'}\n"
        f"🆔 ID: <code>{user.id}</code>"
    )

    try:
        await bot.send_message(
            chat_id=int(ADMIN_ID),
            text=text,
        )
    except Exception as e:
        logger.error("Admin xabari yuborilmadi: %s", e)


@dp.message(Command("start"))
async def start_handler(message: Message):
    user, created = await save_user(message)
    await save_message(message)

    if created:
        await notify_admin(message)

    count = await get_user_count()

    await message.answer(
        f"👋 <b>Assalomu alaykum!</b>\n\n"
        f"💍 Taklifnoma botiga xush kelibsiz!\n\n"
        f"👥 Bot foydalanuvchilari: <b>{count}</b>\n\n"
        f"Kerakli bo'limni tanlang:",
        reply_markup=main_keyboard,
    )


@dp.message(Command("help"))
async def help_handler(message: Message):
    await save_message(message)

    await message.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "Botdan foydalanish uchun pastdagi menyudan kerakli "
        "bo'limni tanlang.",
        reply_markup=main_keyboard,
    )


@dp.message(Command("clear"))
async def clear_handler(message: Message):
    await save_message(message)

    user = message.from_user

    if not user:
        return

    if str(user.id) != str(ADMIN_ID):
        await message.answer(
            "❌ Bu buyruq faqat admin uchun."
        )
        return

    @sync_to_async
    def clear_database():
        BotMessage.objects.all().delete()

    await clear_database()

    await message.answer(
        "🗑 <b>Bot xabarlari tozalandi.</b>"
    )


@dp.message(F.text == "🌐 Saytga o'tish")
async def site_handler(message: Message):
    await save_message(message)

    if SITE_URL:
        await message.answer(
            "🌐 <b>Saytimiz:</b>",
            reply_markup=site_keyboard,
        )
    else:
        await message.answer(
            "⚠️ Sayt manzili hali sozlanmagan."
        )


@dp.message(F.text == "👤 Men haqimda")
async def about_handler(message: Message):
    await save_message(message)

    await message.answer(
        "👤 <b>Men haqimda</b>\n\n"
        "Ism: Asilbek\n"
        "💻 Dasturlash bilan 2024-yildan beri shug'ullanaman.\n\n"
        "🎯 Maqsadim — IT sohasida professional "
        "dasturchi bo'lish."
    )


@dp.message(F.text == "📊 Statistika")
async def statistics_handler(message: Message):
    await save_message(message)

    count = await get_user_count()

    await message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{count}</b>"
    )


@dp.message(F.text == "💬 Bog'lanish")
async def contact_handler(message: Message):
    await save_message(message)

    await message.answer(
        "💬 <b>Bog'lanish</b>\n\n"
        f"👤 Telegram: @{ADMIN_USERNAME}"
    )


@dp.message()
async def fallback_handler(message: Message):
    await save_message(message)

    await message.answer(
        "👇 Iltimos, menyudagi bo'limlardan birini tanlang.",
        reply_markup=main_keyboard,
    )


async def process_update(update_data: dict):
    update = Update.model_validate(update_data)

    await dp.feed_update(
        bot,
        update,
    )


async def close_bot():
    await bot.session.close()