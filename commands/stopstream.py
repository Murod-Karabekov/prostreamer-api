# commands/stopstream.py
from telegram import Update
from telegram.ext import ContextTypes
from commands.pyrogram_client import app
import asyncpg

async def stopstream_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = context.user_data.get("selected_channel_id")
    if not channel_id:
        await query.edit_message_text("Kanal topilmadi ❌")
        return

    try:
        # DB update: is_active = False
        conn = await asyncpg.connect(user="prostreamer", password="secretpassword",
                                     database="prostreamerdb", host="localhost")
        await conn.execute(
            "UPDATE streams SET is_active=FALSE WHERE channel_id=$1 ORDER BY id DESC LIMIT 1",
            int(channel_id)
        )
        await conn.close()

        await query.edit_message_text("Stream to‘xtatildi ⏹")
    except Exception as e:
        await query.edit_message_text(f"Xatolik yuz berdi ❌\n{e}")
