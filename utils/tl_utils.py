import logging
from aiogram.types import ChatMember
from aiogram import Bot
from typing import Optional


async def check_subscription(bot: Bot, user_id: int, link: str) -> bool:
    if not link[1].isdigit():
        username = "@" + link.split("t.me/")[-1]
    else:
        username = link

    logging.info(f"Checking subscription for user {user_id} in chat {username}")

    chat_member = await get_chat_member(bot, user_id, username)

    if isinstance(chat_member, ChatMember) and chat_member.status in [
        "member",
        "administrator",
        "creator",
    ]:
        return True

    return False


async def get_chat_member(
    bot: Bot, user_id: int, username: str
) -> Optional[ChatMember]:
    try:
        chat_member = await bot.get_chat_member(chat_id=username, user_id=user_id)
        return chat_member
    except Exception as e:
        logging.exception(f"Error getting chat member: {e}")
        return None
