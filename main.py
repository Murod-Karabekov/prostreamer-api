import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from commands.start import start
from commands.channel import channel_handler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

App = ApplicationBuilder().token(BOT_TOKEN).build()

App.add_handler(CommandHandler("start", start))
App.add_handler(channel_handler)

App.run_polling()

