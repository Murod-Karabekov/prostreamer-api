import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from commands.start import start
from commands.channel import channel_handler, button_handler_callback
from commands.stream import stream_handler, start_stream_callback_handler, stop_stream_callback_handler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot yaratish
App = ApplicationBuilder().token(BOT_TOKEN).build()

# Command va handlerlarni qo‘shish
App.add_handler(CommandHandler("start", start))
App.add_handler(channel_handler)  # /channel
App.add_handler(button_handler_callback)
App.add_handler(stream_handler)   # /stream
# inline tugmalar

# Start/Stop tugmalari uchun CallbackQueryHandler
App.add_handler(start_stream_callback_handler)
App.add_handler(stop_stream_callback_handler)

# Botni ishga tushirish
App.run_polling()
