# start.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.check_subs import is_subscribed
import asyncpg
import os

REQUIRED_CHANNELS = [
    ("TG Kanal", "karabekov_murod"),
    ("CodeMindClub", "codeMindClub")
]

INSTAGRAM_LINK = "https://www.instagram.com/murod_karabekov/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else ""
    user_id_tg = user.id

    # DB ga foydalanuvchini yozish
    conn = await asyncpg.connect(
        user="prostreamer",
        password="secretpassword",
        database="prostreamerdb",
        host="localhost"
    )
    user_row = await conn.fetchrow("SELECT id FROM users WHERE tg_id=$1", user_id_tg)
    if not user_row:
        await conn.execute(
            "INSERT INTO users(tg_id, username, full_name) VALUES($1, $2, $3)",
            user_id_tg, username, full_name
        )
    await conn.close()

    # Telegram kanalga obuna bo'lish tekshiruvi
    bot = context.bot
    not_subscribed = []
    for title, channel in REQUIRED_CHANNELS:
        ok = await is_subscribed(bot, user_id_tg, channel)
        if not ok:
            not_subscribed.append((title, f"https://t.me/{channel}"))

    if not_subscribed:
        buttons = [[InlineKeyboardButton(title, url=url)] for title, url in not_subscribed]
        buttons.append([InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK)])
        keyboard = InlineKeyboardMarkup(buttons)

        text = (
            f"👋 Salom, {full_name or 'Do‘stim'}!\n\n"
            "Men *Stream Bot*man. Mening yordamimda sen guruh yoki kanalga "
            "kino 🎬 yoki audio 🎵 qo‘yib stream qilishing mumkin.\n\n"
            "➡️ Avval men ishlashim uchun quyidagi kanallarga obuna bo‘lishing shart!,\n"
            "🤷‍♂️Endi shunasan tirikchilik 😅\n"
            "👉 Obuna bo‘lgandan so‘ng qaytib kelib /start ni bos."
        )
        await update.message.reply_text(text, reply_markup=keyboard)
    else:
        text = (
            f"🎉 Xush kelibsan, {full_name or 'Do‘stim'}!\n\n"
            "Sen barcha kanallarga obuna bo‘lgansan. Endi botdan to‘liq foydalanishing mumkin.\n\n"
            "👉 Buyruqlar:\n"
            "/channel - Kanal yoki guruh qo‘shish\n"
            "/stream - Kino yoki audio link yuborish\n"
            "/startstream - Streamni boshlash\n"
            "/stopstream - Streamni to‘xtatish"
        )
        await update.message.reply_text(text)
