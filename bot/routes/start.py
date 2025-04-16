from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, User, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import SQLAlchemyError
from typing import Tuple, Optional

from bot.markup import get_index_inline_keyboard, MyCallback
from db.session import async_session
from utils.db.user import create_or_update_user
from utils.tl_utils import check_subscription
from config import settings
import logging

start_router = Router()
logger = logging.getLogger(__name__)


async def get_subscription_status(
    user: User, bot: Bot
) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    try:
        group_sub_check = True
        channel_sub_check = True

        if settings.GROUP_SUBSCRIPTION_CHECK and settings.GROUP_SUBSCRIPTION_LINK:
            group_sub_check = await check_subscription(
                bot, user.id, settings.GROUP_SUBSCRIPTION_CHECK
            )

        if settings.CHANNEL_SUBSCRIPTION_CHECK and settings.CHANNEL_SUBSCRIPTION_LINK:
            channel_sub_check = await check_subscription(
                bot, user.id, settings.CHANNEL_SUBSCRIPTION_CHECK
            )

        async with async_session() as session:
            try:
                await create_or_update_user(
                    session,
                    chat_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    lang=user.language_code,
                )
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database error updating user {user.id}: {e}")

        if not any(
            [
                settings.GROUP_SUBSCRIPTION_CHECK,
                settings.GROUP_SUBSCRIPTION_LINK,
                settings.CHANNEL_SUBSCRIPTION_CHECK,
                settings.CHANNEL_SUBSCRIPTION_LINK,
            ]
        ):
            return (
                "Добро пожаловать! Это бот с каталогами товаров, выберите один из следующих вариантов:",
                get_index_inline_keyboard(),
            )

        if group_sub_check and channel_sub_check:
            return (
                "Добро пожаловать! Это бот с каталогами товаров, выберите один из следующих вариантов:",
                get_index_inline_keyboard(),
            )

        messages = []
        if not group_sub_check and settings.GROUP_SUBSCRIPTION_LINK:
            messages.append(f"Группа: {settings.GROUP_SUBSCRIPTION_LINK}")
        if not channel_sub_check and settings.CHANNEL_SUBSCRIPTION_LINK:
            messages.append(f"Канал: {settings.CHANNEL_SUBSCRIPTION_LINK}")

        if messages:
            base_message = "⚠️ Для использования бота необходимо подписаться на:"
            return "\n".join([base_message] + messages), None

        return (
            "❌ Требуется подписка, но ссылки для подписки не настроены. Свяжитесь с администратором.",
            None,
        )

    except Exception as e:
        logger.error(f"Error in get_subscription_status for user {user.id}: {e}")
        return (
            "❌ Произошла ошибка при проверке подписки. Пожалуйста, попробуйте позже.",
            None,
        )


@start_router.message(CommandStart())
async def main_menu(message: Message, bot: Bot):
    user = message.from_user
    response_message, keyboard = await get_subscription_status(user, bot)
    try:
        await message.answer(response_message, reply_markup=keyboard)
    except TelegramBadRequest as e:
        logger.error(f"Failed to send message to {user.id}: {e}")
        await message.answer(
            "Произошла ошибка при отображении меню. Пожалуйста, попробуйте снова."
        )


@start_router.callback_query(MyCallback.filter(F.action == "back_to_main_menu"))
async def back_to_main_menu(callback: CallbackQuery, bot: Bot):
    user = callback.from_user
    response_message, keyboard = await get_subscription_status(user, bot)
    try:
        await callback.message.edit_text(response_message, reply_markup=keyboard)
        await callback.answer()
    except TelegramBadRequest as e:
        logger.error(f"Failed to edit message for {user.id}: {e}")
        await callback.answer("Произошла ошибка при обновлении меню.", show_alert=True)
