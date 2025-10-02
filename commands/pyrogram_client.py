# commands/pyrogram_client.py
import os
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")  # session/prostreamer.session

if not API_ID or not API_HASH or not SESSION_NAME:
    raise ValueError("❌ API_ID, API_HASH yoki SESSION_NAME .env faylda topilmadi!")

# Global app instance, har doim shu sessiya bilan ishlaydi
app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
