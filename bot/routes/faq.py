from aiogram import Router, F
from aiogram.filters.callback_data import CallbackQuery

from db.session import async_session
from bot.markup import (
    MyCallback,
    get_faq_slider,
    get_back_to_main_menu,
    get_back_to_faq,
)
from utils.db.faq import get_all_faqs, count_faqs, get_faq_by_id

faq_router = Router()


@faq_router.callback_query(MyCallback.filter(F.action == "faq"))
async def faq_main_menu_handler(
    callback_query: CallbackQuery, page: int = 0, per_page: int = 5
):
    async with async_session() as session:
        total_faqs = await count_faqs(session)
        total_pages = (total_faqs + per_page - 1) // per_page
        faqs = await get_all_faqs(session, page, per_page)

    if not faqs:
        await callback_query.message.edit_text(
            "Нет доступных часто задаваемых вопросов.",
            reply_markup=get_back_to_main_menu(),
        )
        return

    await callback_query.message.edit_text(
        "Вот часто задаваемые вопросы:",
        reply_markup=get_faq_slider(faqs, page, total_pages, per_page),
    )


@faq_router.callback_query(MyCallback.filter(F.action.startswith("faq_page_")))
async def handle_faq_page_navigation(callback_query: CallbackQuery, per_page: int = 5):
    action = callback_query.data.split("_")
    page = int(action[-1])

    async with async_session() as session:
        total_faqs = await count_faqs(session)
        total_pages = (total_faqs + per_page - 1) // per_page
        faqs = await get_all_faqs(session, page, per_page)

    await callback_query.message.edit_text(
        "Вот часто задаваемые вопросы:",
        reply_markup=get_faq_slider(faqs, page, total_pages, per_page),
    )


@faq_router.callback_query(MyCallback.filter(F.action.startswith("faq_item_")))
async def handle_faq_item(callback_query: CallbackQuery):
    faq_id = int(callback_query.data.split("_")[-1])

    async with async_session() as session:
        faq = await get_faq_by_id(session, faq_id)

    if not faq:
        await callback_query.message.edit_text(
            "Вопрос не найден.", reply_markup=get_back_to_faq()
        )
        return

    await callback_query.message.edit_text(
        f"Заголовок: {faq.title}\n\n{faq.text}", reply_markup=get_back_to_faq()
    )
