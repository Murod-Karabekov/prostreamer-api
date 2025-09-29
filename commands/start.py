from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.check_subs import is_subscribed

REQUIRED_CHANNELS = [
    ("TG Kanal", "karabekov_murod"),
    ("CodeMindClub", "codeMindClub")
]

INSTAGRAM_LINK = "https://www.instagram.com/murod_karabekov/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "Do‘stim"
    bot = context.bot
    user_id = user.id

    not_subscribed = []
    for title, channel in REQUIRED_CHANNELS:
        ok = await is_subscribed(bot, user_id, channel)
        if not ok:
            not_subscribed.append((title, f"https://t.me/{channel}"))

    if not_subscribed:
        buttons = [[InlineKeyboardButton(title, url=url)] for title, url in not_subscribed]
        buttons.append([InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK)])
        
        keyboard = InlineKeyboardMarkup(buttons)

        text = ( f"👋 Salom, {name}!\n\n" 
                "Men *Stream Bot*man. Mening yordamimda sen guruh yoki kanalga " 
                "kino 🎬 yoki audio 🎵 qo‘yib stream qilishing mumkin.\n\n" 
                "➡️ Avval men ishlashim uchun quyidagi kanallarga obuna bo‘lishing shart!,\n" 
                "🤷‍♂️Endi shunasan tirikchilik 😅\n" 
                "👉 Obuna bo‘lgandan so‘ng qaytib kelib /start ni bos." )
        await update.message.reply_text(text, reply_markup=keyboard)
    else:
        text = (
            f"🎉 Xush kelibsan, {name}!\n\n"
            "Sen barcha kanallarga obuna bo‘lgansan. Endi botdan to‘liq foydalanishing mumkin.\n\n"
            "👉 Buyruqlar:\n"
            "/channel - Kanal yoki guruh qo‘shish\n"
            "/stream - Kino yoki audio link yuborish\n"
            "/startstream - Streamni boshlash\n"
            "/stopstream - Streamni to‘xtatish"
        )
        await update.message.reply_text(text)
