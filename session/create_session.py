import os
from telethon import TelegramClient
from dotenv import load_dotenv

# .env fayldan ma'lumotlarni yuklaymiz
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

if not API_ID or not API_HASH:
    raise ValueError("❌ API_ID yoki API_HASH .env faylda topilmadi!")

# Sessiyani yaratish uchun client
client = TelegramClient("session/prostreamer", API_ID, API_HASH)

async def main():
    print("📲 Telegram sessiya yaratish jarayoni boshlandi...")
    await client.start()
    print("✅ Sessiya muvaffaqiyatli yaratildi va 'session/prostreamer.session' faylida saqlandi.")

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
