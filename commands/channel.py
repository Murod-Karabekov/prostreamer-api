# channel.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters, ContextTypes
import asyncpg

ASK_LINK = 1

async def channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Iltimos, kanal yoki guruh linkini yuboring (https://t.me/kanal yoki @kanal_nomi):"
    )
    return ASK_LINK

async def save_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    link = update.message.text.strip()
    bot = context.bot

    if not (link.startswith("https://t.me/") or link.startswith("@")):
        await update.message.reply_text("Faqat Telegram kanal yoki guruh linkini yuboring!")
        return ASK_LINK

    # username ajratib olish
    username = link.split("/")[-1] if link.startswith("https://t.me/") else link
    if not username.startswith("@"):
        username = "@" + username

    # Kanal haqida to‘liq ma’lumot olish
    try:
        chat = await bot.get_chat(username)
        chat_id = chat.id
    except Exception as e:
        await update.message.reply_text(f"Kanalni topib bo‘lmadi: {e}")
        return ConversationHandler.END

    # Adminligini tekshirish
    try:
        chat_member = await bot.get_chat_member(username, user.id)
        if chat_member.status not in ["administrator", "creator"]:
            await update.message.reply_text("Siz bu kanalning admini emassiz! Stream qila olmaysiz.")
            return ConversationHandler.END
    except:
        await update.message.reply_text("Bot kanalga admin qilinmagan!")
        return ConversationHandler.END

    # DB ga ulanish
    conn = await asyncpg.connect(
        user="prostreamer",
        password="secretpassword",
        database="prostreamerdb",
        host="localhost"
    )

    # Foydalanuvchini DB ga qo‘shish
    user_row = await conn.fetchrow("SELECT id FROM users WHERE tg_id=$1", user.id)
    if not user_row:
        user_row = await conn.fetchrow(
            "INSERT INTO users(tg_id, username, full_name) VALUES($1, $2, $3) RETURNING id",
            user.id, f"@{user.username}" if user.username else "", f"{user.first_name or ''} {user.last_name or ''}".strip()
        )
    user_id = user_row["id"]

    # Kanalni DB ga qo‘shish
    await conn.execute(
        """
        INSERT INTO channels(user_id, channel_name, channel_link, channel_id)
        VALUES($1, $2, $3, $4)
        ON CONFLICT (channel_link) DO UPDATE SET channel_id = EXCLUDED.channel_id
        """,
        user_id, username, username, chat_id
    )
    await conn.close()

    # Inline tugma
    buttons = [
        [InlineKeyboardButton("🎥 Stream boshlash", callback_data="go_stream")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        f"Kanal muvaffaqiyatli qo‘shildi: {username}\n\n"
        "Endi shu kanal uchun streamni boshlashingiz mumkin 👇",
        reply_markup=keyboard
    )
    return ConversationHandler.END

# CallbackQueryHandler uchun tugma
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "go_stream":
        from commands.stream import stream_start
        # Callback orqali kelgan message ni bevosita yuboramiz
        context._update = query.message  # bu shunchaki kerak bo‘lsa
        return await stream_start(query.message, context)


# ConversationHandler
channel_handler = ConversationHandler(
    entry_points=[CommandHandler("channel", channel)],
    states={ASK_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_channel)]},
    fallbacks=[]
)

# Tugma uchun alohida CallbackQueryHandler
button_handler_callback = CallbackQueryHandler(button_handler, pattern="^go_stream$")
