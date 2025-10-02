from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
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

    username = link.split("/")[-1] if link.startswith("https://t.me/") else link
    if not username.startswith("@"):
        username = "@" + username

    try:
        chat = await bot.get_chat(username)
        chat_id = chat.id
    except Exception as e:
        await update.message.reply_text(f"Kanalni topib bo‘lmadi: {e}")
        return ConversationHandler.END

    try:
        chat_member = await bot.get_chat_member(username, user.id)
        if chat_member.status not in ["administrator", "creator"]:
            await update.message.reply_text("Siz bu kanalning admini emassiz! Stream qila olmaysiz.")
            return ConversationHandler.END
    except:
        await update.message.reply_text("Bot kanalga admin qilinmagan!")
        return ConversationHandler.END

    conn = await asyncpg.connect(
        user="prostreamer",
        password="secretpassword",
        database="prostreamerdb",
        host="localhost"
    )

    user_row = await conn.fetchrow("SELECT id FROM users WHERE tg_id=$1", user.id)
    if not user_row:
        user_row = await conn.fetchrow(
            "INSERT INTO users(tg_id, username, full_name) VALUES($1, $2, $3) RETURNING id",
            user.id, f"@{user.username}" if user.username else "", f"{user.first_name or ''} {user.last_name or ''}".strip()
        )
    user_id = user_row["id"]

    await conn.execute(
        """
        INSERT INTO channels(user_id, channel_name, channel_link, channel_id)
        VALUES($1, $2, $3, $4)
        ON CONFLICT (channel_link) DO UPDATE SET channel_id = EXCLUDED.channel_id
        """,
        user_id, username, username, chat_id
    )
    await conn.close()

    await update.message.reply_text(
        f"Kanal muvaffaqiyatli qo‘shildi: {username}\n\n"
        "Endi /stream komandasini yozib, stream linkni yuborishingiz mumkin."
    )
    return ConversationHandler.END


channel_handler = ConversationHandler(
    entry_points=[CommandHandler("channel", channel)],
    states={ASK_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_channel)]},
    fallbacks=[]
)
