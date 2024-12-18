from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, LabeledPrice
from aiogram.filters.state import State, StatesGroup, StateFilter

from db.session import async_session
from utils.db.cart import (
    get_cart_item_by_id,
    delete_cart_item_by_id,
    update_cart_by_id,
    count_cart_items,
    get_cart_by_user_id,
)
from utils.log import logger
from utils.xl_utils import generate_order_data, write_order_to_excel
from bot.markup import (
    MyCallback,
    get_cart_slider,
    get_back_to_main_menu,
    get_product_actions,
)
from schemas.cart import CartUpdateSchema
from config import settings


class CartState(StatesGroup):
    waiting_for_address = State()


cart_router = Router()


@cart_router.callback_query(MyCallback.filter(F.action == "cart"))
async def cart_slider_handler(
    callback_query: CallbackQuery, page: int = 0, per_page: int = 5
):
    user_id = callback_query.from_user.id

    async with async_session() as session:
        cart_items = await get_cart_by_user_id(
            session, user_id, page=page, per_page=per_page
        )
        total_items = await count_cart_items(session, user_id)

    if not cart_items:
        await callback_query.message.edit_text(
            "Ваша корзина пуста.", reply_markup=get_back_to_main_menu()
        )
        return

    total_pages = (total_items + per_page - 1) // per_page
    await callback_query.message.edit_text(
        "Ваши товары в корзине:",
        reply_markup=get_cart_slider(cart_items, page, total_pages, per_page),
    )


@cart_router.callback_query(MyCallback.filter(F.action.startswith("cart_page_")))
async def handle_cart_page_navigation(callback_query: CallbackQuery, per_page: int = 5):
    action = callback_query.data.split("_")
    page = int(action[-1])

    user_id = callback_query.from_user.id

    async with async_session() as session:
        cart_items = await get_cart_by_user_id(
            session, user_id, page=page, per_page=per_page
        )
        total_items = await count_cart_items(session, user_id)

    if not cart_items:
        await callback_query.message.edit_text(
            "Ваша корзина пуста.", reply_markup=get_back_to_main_menu()
        )
        return

    total_pages = (total_items + per_page - 1) // per_page

    keyboard = get_cart_slider(cart_items, page, total_pages, per_page)
    await callback_query.message.edit_text(
        "Ваши товары в корзине:", reply_markup=keyboard
    )


@cart_router.callback_query(MyCallback.filter(F.action.startswith("cart_item_")))
async def handle_cart_item_options(callback_query: CallbackQuery):
    action = callback_query.data.split("_")
    cart_id = int(action[-1])

    await callback_query.message.edit_text(
        text="Выберите действие с товаром:",
        reply_markup=get_product_actions(cart_id),
    )


@cart_router.callback_query(MyCallback.filter(F.action.startswith("cart_delete_")))
async def delete_cart_item_handler(callback_query: CallbackQuery):
    cart_id = int(callback_query.data.split("_")[-1])

    async with async_session() as session:
        await delete_cart_item_by_id(session, cart_id)

    await callback_query.answer("Товар удален из корзины.")
    await cart_slider_handler(callback_query)


@cart_router.callback_query(MyCallback.filter(F.action.startswith("cart_address_")))
async def specify_cart_address(
    callback_query: CallbackQuery, state: FSMContext, bot: Bot
):
    cart_id = int(callback_query.data.split("_")[-1])
    await state.update_data(cart_id=cart_id)
    user_data = await state.get_data()
    last_message_id = user_data.get("last_message_id")

    if last_message_id:
        await bot.delete_message(
            chat_id=callback_query.from_user.id, message_id=last_message_id
        )

    message = await callback_query.message.edit_text("Введите адрес доставки:")
    await state.update_data(last_message_id=message.message_id)
    await state.set_state(CartState.waiting_for_address)


@cart_router.message(StateFilter(CartState.waiting_for_address))
async def handle_address_input(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    address = message.text.strip()

    user_data = await state.get_data()
    cart_id = user_data.get("cart_id")
    last_message_id = user_data.get("last_message_id")

    if last_message_id:
        await bot.delete_message(chat_id=user_id, message_id=last_message_id)

    if not address:
        response_message = await message.reply("Пожалуйста, введите корректный адрес.")
        await state.update_data(last_message_id=response_message.message_id)
        return

    async with async_session() as session:
        await update_cart_by_id(
            session,
            CartUpdateSchema(id=cart_id, address=address),
        )

    cart_item = await get_cart_item_by_id(session, cart_id)
    prices = [
        LabeledPrice(
            label=cart_item.product_name,
            amount=int(cart_item.cost * 100),
        )
    ]
    await state.clear()
    invoice_message = await message.answer_invoice(
        title="Ваш заказ",
        description=f"Введенный адрес доставки: {address}. Оплата вашего заказа.",
        prices=prices,
        payload="demo",
        currency="RUB",
        provider_token=settings.BOT_PAYMENT_PROVIDER_TOKEN,
    )

    await state.update_data(
        {"last_message_id": invoice_message.message_id, "cart_id": cart_id}
    )


@cart_router.pre_checkout_query(lambda query: True)
async def checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(
        ok=True,
        error_message="Произошла ошибка при оплате картой, попробуйте чуть позже",
    )


@cart_router.message(F.content_type == F.content_type.SUCCESSFUL_PAYMENT)
async def got_payment(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    user_data = await state.get_data()
    last_message_id = user_data.get("last_message_id")
    cart_id = user_data.get("cart_id")

    if last_message_id:
        await bot.delete_message(chat_id=user_id, message_id=last_message_id)

    if last_message_id:
        await message.answer(
            text="Оплата прошла успешно",
            reply_markup=get_back_to_main_menu(),
        )
    else:
        await message.answer(
            "Оплата прошла успешно", reply_markup=get_back_to_main_menu()
        )

    async with async_session() as session:
        cart_item = await get_cart_item_by_id(session, cart_id)

        order_data = generate_order_data(
            user_id=user_id,
            product_id=cart_item.product_id,
            product_name=cart_item.product_name,
            quantity=cart_item.amount,
            price=cart_item.cost,
            address=cart_item.address,
        )

        await write_order_to_excel(order_data)

        await update_cart_by_id(
            session, CartUpdateSchema(id=cart_id, is_being_delivered=True)
        )
    await state.clear()
