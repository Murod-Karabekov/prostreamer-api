from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes
import asyncpg

from commands.startstream import startstream_handler, stopstream_handler

ASK_LINK, ASK_CHANNEL = range(2)

async def stream_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Iltimos, stream qilmoqchi bo‘lgan video yoki audio linkini yuboring:")
    return ASK_LINK

async def save_stream_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    link = update.message.text.strip()
    context.user_data['stream_link'] = link

    # DB dan foydalanuvchining kanallarini olish
    conn = await asyncpg.connect(user="prostreamer", password="secretpassword",
                                 database="prostreamerdb", host="localhost")
    channels = await conn.fetch("SELECT id, channel_name FROM channels WHERE user_id=(SELECT id FROM users WHERE tg_id=$1)", user.id)
    await conn.close()

    if not channels:
        await update.message.reply_text("Sizda qo‘shilgan kanal yo‘q. Avval /channel orqali kanal qo‘shing.")
        return ConversationHandler.END

    buttons = [[InlineKeyboardButton(ch['channel_name'], callback_data=str(ch['id']))] for ch in channels]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Qaysi kanalga stream qilmoqchisiz?", reply_markup=keyboard)
    return ASK_CHANNEL

async def choose_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    channel_id = int(query.data)
    stream_link = context.user_data['stream_link']

    # DB ga saqlash
    conn = await asyncpg.connect(user="prostreamer", password="secretpassword",
                                 database="prostreamerdb", host="localhost")
    await conn.execute("INSERT INTO streams(channel_id, stream_url) VALUES($1, $2)", channel_id, stream_link)
    await conn.close()

    # Start / Stop tugmalari
    buttons = [
        [InlineKeyboardButton("▶️ Start Stream", callback_data="start_stream"),
         InlineKeyboardButton("⏹ Stop Stream", callback_data="stop_stream")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(f"Stream link muvaffaqiyatli saqlandi! ✅\nLink: {stream_link}", reply_markup=keyboard)
    return ConversationHandler.END

stream_handler = ConversationHandler(
    entry_points=[CommandHandler("stream", stream_start)],
    states={
        ASK_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_stream_link)],
        ASK_CHANNEL: [CallbackQueryHandler(choose_channel)]
    },
    fallbacks=[]
)

# Start / Stop tugmalari callback
start_stream_callback_handler = CallbackQueryHandler(startstream_handler, pattern="^start_stream$")
stop_stream_callback_handler = CallbackQueryHandler(stopstream_handler, pattern="^stop_stream$")
