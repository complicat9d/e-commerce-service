import logging
import os

from aiogram.types import ChatMember, InputFile, FSInputFile
from aiogram import Bot
from typing import Optional

logger = logging.getLogger(__name__)


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


async def send_message_to_telegram(
    bot: Bot, user_id: str, text: str, photo_path: str = None
):
    try:
        if photo_path:
            await bot.send_photo(user_id, photo=FSInputFile(photo_path), caption=text)
        else:
            await bot.send_message(user_id, text)
    except Exception as e:
        logging.error(f"Error sending message to {user_id}: {e}")
