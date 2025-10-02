# commands/stopstream.py
from telegram import Update
from telegram.ext import ContextTypes
from commands.startstream import pytg  # mavjud pytg instance

async def stopstream_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    try:
        await pytg.leave_group_call(chat_id)
        await query.edit_message_text("⏹ Stream to‘xtatildi.")
    except Exception as e:
        await query.edit_message_text(f"❌ Xato: {e}")
