# commands/startstream.py
from telegram import Update
from telegram.ext import ContextTypes
from pyrogram import errors, raw, types
from commands.pyrogram_client import app
import asyncpg

async def startstream_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = context.user_data.get("selected_channel_id")
    if not channel_id:
        await query.edit_message_text("Kanal topilmadi ❌")
        return

    try:
        # Client start qilinadi (agar ishga tushmagan bo‘lsa)
        if not app.is_connected:
            await app.start()

        # Chat obyektini olish va access_hash bilan peer yaratish
        chat = await app.get_chat(channel_id)
        if not hasattr(chat, "access_hash"):
            await query.edit_message_text("Kanal ma'lumotlari to‘liq emas ❌")
            return

        peer = types.InputPeerChannel(channel_id=chat.id, access_hash=chat.access_hash)

        # Videochat yaratish
        await app.invoke(
            raw.functions.phone.CreateGroupCall(
                peer=peer,
                random_id=0,
                title="Bot Stream Videochat"
            )
        )

        # DB update: is_active = TRUE
        conn = await asyncpg.connect(
            user="prostreamer", password="secretpassword",
            database="prostreamerdb", host="localhost"
        )
        await conn.execute(
            "UPDATE streams SET is_active=TRUE WHERE channel_id=$1 ORDER BY id DESC LIMIT 1",
            channel_id
        )
        await conn.close()

        await query.edit_message_text("Stream boshlandi ✅ Videochat ochildi!")

    except errors.PeerIdInvalid:
        await query.edit_message_text(
            "Kanal ID noto‘g‘ri yoki userbot admin emas ❌\n"
            "Iltimos, userbotni kanalga admin qiling va ruxsatlarni tekshiring."
        )
    except Exception as e:
        await query.edit_message_text(f"Xatolik yuz berdi ❌\n{e}")
