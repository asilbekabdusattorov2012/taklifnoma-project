import asyncio
import logging
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bosh_sahifa.settings")
django.setup()

from django.conf import settings
from asgiref.sync import sync_to_async
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from bosh_sahifa2.models import BotUser, BotMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
ADMIN_ID = settings.TELEGRAM_ADMIN_ID
ADMIN_USERNAME = getattr(settings, "TELEGRAM_ADMIN_USERNAME", "")
SITE_URL = settings.SITE_URL

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN .env faylda sozlanmagan.")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌐 saytga otish")],
        [KeyboardButton(text="👤 Men haqimda")],
        [KeyboardButton(text="💬 Bog'lanish")],
    ], resize_keyboard=True
)

site_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🌐 Taklifnoma saytini ochish", url=SITE_URL)]]
)

@sync_to_async
def save_user(user):
    """Foydalanuvchini bazaga saqlaydi va yangi foydalanuvchi ekanini qaytaradi."""
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
def clear_users():
    return BotUser.objects.all().delete()


@sync_to_async
def remember_message(chat_id, message_id):
    BotMessage.objects.create(chat_id=chat_id, message_id=message_id)

async def answer_and_remember(message: Message, text: str, **kwargs):
    sent = await message.answer(text, **kwargs)
    await remember_message(sent.chat.id, sent.message_id)
    return sent

@sync_to_async
def get_all_saved_messages():
    return list(BotMessage.objects.values_list("chat_id", "message_id"))

@sync_to_async
def delete_all_saved_message_records():
    BotMessage.objects.all().delete()

@dp.message(Command("start"))
async def start_handler(message: Message):
    is_new = await save_user(message.from_user)
    count = await user_count()
    await notify_admin_about_new_user(message, is_new)

    name = (message.from_user.first_name or "mehmon").strip()
    username_note = "" if message.from_user.username else "\n\n⚠️ <b>Eslatma:</b> buyurtma berishda Telegram username kerak bo‘ladi. Agar username qo‘yilmagan bo‘lsa, Telegram sozlamalaridan username o‘rnating."
    await answer_and_remember(message,
        f"💌 <b>Taklifnoma</b>  •  👤 <b>User: {count} ta</b>\n\n"
        f"Assalomu alaykum, <b>{name}</b>! 👋\n\n"
        "Chiroyli taklifnoma shablonlarini ko‘ring va sayt orqali buyurtma bering. 😊"
        f"{username_note}\n\n"
        "👇 Kerakli bo‘limni tanlang:",
        reply_markup=main_keyboard,
    )

@dp.message(Command("help"))
async def help_handler(message: Message):
    await save_user(message.from_user)
    await answer_and_remember(message, "ℹ️ <b>Yordam</b>\n\n🌐 Sayt orqali shablon tanlang va buyurtma bering.\n📱 Buyurtma uchun Telegram username kerak.\n💬 Savolingiz bo‘lsa, Bog'lanish bo‘limidan foydalaning.\n\n/start — asosiy menyu")

async def notify_admin_about_new_user(message: Message, is_new: bool):
    """Yangi foydalanuvchi haqida xabarni faqat bot egasiga yuboradi."""
    if not is_new or not ADMIN_ID:
        return

    username = f"@{message.from_user.username}" if message.from_user.username else "username yo‘q"
    count = await user_count()
    text = (
        "👤 <b>YANGI FOYDALANUVCHI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🧑 Ism: {message.from_user.first_name or '—'}\n"
        f"🔗 Username: {username}\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"👥 Jami foydalanuvchilar: <b>{count} ta</b>\n"
        f"👑 Admin: {ADMIN_USERNAME or 'bot egasi'}"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=text)
    except Exception as exc:
        logger.warning("Admin xabari yuborilmadi: %s", exc)


@dp.message(Command("clear"))
async def clear_handler(message: Message):
    if not ADMIN_ID or str(message.from_user.id) != str(ADMIN_ID):
        await answer_and_remember(message, "⛔ Bu buyruq faqat bot egasi uchun.")
        return

    # /clear statistikani o‘chirmaydi. Baza ichida saqlangan BOT xabarlarini
    # barcha chatlar bo‘yicha o‘chirishga urinadi. Foydalanuvchi xabarlarini
    # Telegram Bot API orqali shaxsiy chatlardan o‘chirish mumkin emas.
    saved_messages = await get_all_saved_messages()
    deleted_count = 0
    failed_count = 0

    for chat_id, message_id in saved_messages:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            deleted_count += 1
        except Exception as e:
            failed_count += 1
            logger.warning("Bot xabarini o‘chirib bo‘lmadi (%s, %s): %s", chat_id, message_id, e)

    await delete_all_saved_message_records()

    await message.answer(
        f"✅ Botning saqlangan eski xabarlari o‘chirildi. ({deleted_count} ta)",
        reply_markup=main_keyboard,
    )

@dp.message(F.text == "🌐 Saytga o'tish")
async def website_handler(message: Message):
    await save_user(message.from_user)
    await answer_and_remember(message, "🌐 <b>Taklifnoma sayti</b>\n\nQuyidagi tugmani bosing:", reply_markup=site_keyboard)

@dp.message(F.text == "👤 Men haqimda")
async def about_handler(message: Message):
    await save_user(message.from_user)
    count = await user_count()
    text = """👨‍💻 <b>Men haqimda</b>

Mening ismim Asilbek. Men dasturiy ta’minot yaratish bilan shug‘ullanaman va IT sohasida o‘z bilim va ko‘nikmalarimni rivojlantirib kelmoqdaman. Dasturlash bo‘yicha faoliyatimni 2024-yildan boshlaganman.

Asosiy yo‘nalishim — foydalanuvchilar uchun qulay va zamonaviy dasturlar yaratish. Men doimo yangi bilimlarni o‘rganishga va o‘z ustimda ishlashga intilaman.

Hozirgi asosiy maqsadim — IT sohasi bo‘yicha sertifikat olish va kelajakda kiberxavfsizlik yo‘nalishida professional faoliyat yuritish. Bu soha menga qiziq, chunki texnologiyalar va xavfsizlik masalalarini o‘rganishni yoqtiraman.

Men keng fikrlashga, muammolarga turli nuqtayi nazardan yondashishga va yangi yechimlar topishga harakat qilaman. Bugungi kungacha frontend va backend yo‘nalishlarini o‘rganganim mening muhim yutuqlarimdan biridir.

Kelajakdagi maqsadim — IT va kiberxavfsizlik sohasida kuchli mutaxassis bo‘lib, foydalanuvchilar uchun foydali, xavfsiz va zamonaviy dasturiy yechimlar yaratish.

👤 <b>Bot foydalanuvchilari: COUNT ta</b>""".replace("COUNT", str(count))
    await answer_and_remember(message, text)

@dp.message(F.text == "💬 Bog'lanish")
async def contact_handler(message: Message):
    await save_user(message.from_user)
        
    await answer_and_remember(message, f"💬 <b>Bog'lanish</b>\n\nSavolingiz bo‘lsa, 👑 Admin: {ADMIN_USERNAME or 'bot egasi'} shu havolaga yozsalaring bo'ladi😊\n\nBuyurtma berish uchun avval 🌐 <b>Saytga o‘tish</b> tugmasini bosing.")

@dp.message()
async def fallback_handler(message: Message):
    await save_user(message.from_user)
    await answer_and_remember(message, "Tushunmadim 🙂\nPastdagi menyudan kerakli bo'limni tanlang.", reply_markup=main_keyboard)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Telegram bot ishga tushdi.")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
