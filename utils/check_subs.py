async def is_subscribed(bot, user_id, channel_username):
    """Foydalanuvchi kanalga obuna bo‘lganini tekshiradi"""
    try:
        member = await bot.get_chat_member(f"@{channel_username}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False
