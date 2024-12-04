from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, User

from bot.markup import get_index_inline_keyboard, MyCallback
from db.session import async_session
from utils.db.user import create_or_update_user
from utils.tl_utils import check_subscription
from config import settings

start_router = Router()


async def get_subscription_status(user: User, bot: Bot):
    group_sub_check = await check_subscription(
        bot, user.id, settings.GROUP_SUBSCRIPTION_CHECK
    )
    channel_sub_check = await check_subscription(
        bot, user.id, settings.CHANNEL_SUBSCRIPTION_CHECK
    )

    if group_sub_check and channel_sub_check:
        response_message = "Добро пожаловать! Это бот с каталогами товаров, выберите один из следующих вариантов:"
        keyboard = get_index_inline_keyboard()
        async with async_session() as session:
            await create_or_update_user(
                session,
                chat_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                lang=user.language_code,
            )
    elif group_sub_check and not channel_sub_check:
        response_message = (
            "⚠️ Вы подписаны на группу, но вам нужно подписаться на канал, чтобы продолжить.\n"
            f"Пожалуйста, подпишитесь на канал здесь: {settings.CHANNEL_SUBSCRIPTION_LINK}"
        )
        keyboard = None
    elif not group_sub_check and channel_sub_check:
        response_message = (
            "⚠️ Вы подписаны на канал, но вам нужно подписаться на группу, чтобы продолжить.\n"
            f"Пожалуйста, подпишитесь на группу здесь: {settings.GROUP_SUBSCRIPTION_LINK}"
        )
        keyboard = None
    else:
        response_message = (
            "❌ Вы не подписаны ни на группу, ни на канал. Пожалуйста, подпишитесь на оба, чтобы продолжить.\n"
            f"Пожалуйста, подпишитесь на группу и канал:\n"
            f"Группа: {settings.GROUP_SUBSCRIPTION_LINK}\n"
            f"Канал: {settings.CHANNEL_SUBSCRIPTION_LINK}"
        )
        keyboard = None

    return response_message, keyboard


@start_router.message(CommandStart())
async def main_menu(message: Message, bot: Bot):
    user = message.from_user
    response_message, keyboard = await get_subscription_status(user, bot)
    await message.answer(response_message, reply_markup=keyboard)


@start_router.callback_query(MyCallback.filter(F.action == "back_to_main_menu"))
async def back_to_main_menu(callback_query: CallbackQuery, bot: Bot):
    user = callback_query.from_user
    response_message, keyboard = await get_subscription_status(user, bot)
    await callback_query.message.edit_text(response_message, reply_markup=keyboard)
    await callback_query.answer()
