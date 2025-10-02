from telegram import Update
from telegram.ext import ContextTypes

async def startstream_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Start bosildi ✅")
    await query.edit_message_text("Stream START qilindi! 🎬")

async def stopstream_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Stop bosildi ⏹")
    await query.edit_message_text("Stream STOP qilindi! 🛑")
