from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import State, StatesGroup, StateFilter


from bot.markup import (
    MyCallback,
    get_category_slider,
    get_product_slider,
    get_back_to_category,
    get_back_to_catalog,
    get_product_menu,
    get_back_to_main_menu_keyboard,
)
from db.session import async_session
from utils.db.category import get_all_categories, count_categories
from utils.db.product import (
    get_all_products_by_category,
    get_product_by_id,
    count_products,
)
from utils.db.cart import create_cart_item
from utils.log import logger
from schemas.cart import CartCreateSchema
from schemas.exc import InsufficientStockException


class CartState(StatesGroup):
    waiting_for_quantity = State()


category_slider = Router()


@category_slider.callback_query(MyCallback.filter(F.action == "catalog"))
async def catalog_slider_handler(
    callback_query: CallbackQuery, page: int = 0, per_page: int = 5
):
    async with async_session() as session:
        categories = await get_all_categories(session, page, per_page)
        total_categories = await count_categories(session)
        amount_of_pages = (total_categories + per_page - 1) // per_page

    logger.info(
        "In 'catalog' callback: page: {}, amount_of_pages: {}".format(
            page, amount_of_pages
        )
    )
    if not categories:
        await callback_query.message.edit_text(
            text="Категории не найдены.", reply_markup=get_back_to_catalog()
        )
        return

    keyboard = get_category_slider(
        categories=categories,
        page=page,
        amount_of_pages=amount_of_pages,
        objects_per_page=per_page,
    )

    await callback_query.message.edit_text("Выберите категорию:", reply_markup=keyboard)


@category_slider.callback_query(
    MyCallback.filter(F.action.startswith("category_page_"))
)
async def handle_category_page_navigation(
    callback_query: CallbackQuery, per_page: int = 5
):
    action = callback_query.data.split("_")
    page = int(action[-1])

    async with async_session() as session:
        categories = await get_all_categories(session, page, per_page)

    if not categories:
        await callback_query.message.edit_text(
            text="Категории недоступны.", reply_markup=get_back_to_catalog()
        )
        return

    total_categories = await count_categories(session)
    amount_of_pages = (total_categories + per_page - 1) // per_page

    logger.info(
        "In 'category_page_' callback: page: {}, amount_of_pages: {}".format(
            page, amount_of_pages
        )
    )
    keyboard = get_category_slider(
        categories=categories,
        page=page,
        amount_of_pages=amount_of_pages,
        objects_per_page=per_page,
    )

    await callback_query.message.edit_text("Выберите категорию:", reply_markup=keyboard)


@category_slider.callback_query(MyCallback.filter(F.action.startswith("category_")))
async def handle_category_selection(
    callback_query: CallbackQuery, page: int = 0, per_page: int = 5
):
    category_id = int(callback_query.data.split("_")[-1])
    logger.info("'category_id': {}; 'page': {}".format(category_id, page))
    async with async_session() as session:
        products = await get_all_products_by_category(session, category_id)
        total_products = await count_products(session)

    if products:
        amount_of_pages = (total_products + per_page - 1) // per_page

        keyboard = get_product_slider(
            products=products,
            page=page,
            amount_of_pages=amount_of_pages,
            objects_per_page=per_page,
            category_id=category_id,
        )

        await callback_query.message.edit_text(
            text=f"Категория выбрана. Выберите продукт:",
            reply_markup=keyboard,
        )
    else:
        await callback_query.message.edit_text(
            text="В этой категории нет продуктов.", reply_markup=get_back_to_catalog()
        )


@category_slider.callback_query(MyCallback.filter(F.action.startswith("product_page_")))
async def handle_product_page_navigation(
    callback_query: CallbackQuery, per_page: int = 5
):
    action = callback_query.data.split("_")
    page = int(action[-1])

    category_id = int(action[-2])
    logger.info(
        "'category_id': {}; 'page': {}; action: {}".format(category_id, page, action)
    )
    async with async_session() as session:
        products = await get_all_products_by_category(session, category_id)
        total_products = await count_products(session)

    if not products:
        await callback_query.message.edit_text(
            text="Продукты недоступны.",
            reply_markup=get_back_to_category(category_id),
        )
        return

    amount_of_pages = (total_products + per_page - 1) // per_page

    keyboard = get_product_slider(
        products=products,
        page=page,
        amount_of_pages=amount_of_pages,
        objects_per_page=per_page,
        category_id=category_id,
    )

    await callback_query.message.edit_text(
        "Категория выбрана. Выберите продукт:", reply_markup=keyboard
    )


@category_slider.callback_query(MyCallback.filter(F.action.startswith("product_")))
async def handle_product_selection(callback_query: CallbackQuery):
    product_id = int(callback_query.data.split("_")[-1])

    async with async_session() as session:
        product = await get_product_by_id(session, product_id)

    if product:
        await callback_query.message.edit_text(
            text=f"Вы выбрали продукт: {product.name}\nОписание: {product.description}\nЦена: {product.cost}₽",
            reply_markup=get_product_menu(product.category_id, product_id),
        )
    else:
        await callback_query.message.edit_text(
            text="Продукты недоступны.",
            reply_markup=get_back_to_category(product.category_id),
        )


@category_slider.callback_query(MyCallback.filter(F.action == "back_to_category"))
async def back_to_category(
    callback_query: CallbackQuery, page: int = 0, per_page: int = 5
):
    category_id = int(callback_query.data.split("_")[-1])

    async with async_session() as session:
        products = await get_all_products_by_category(session, category_id)
        total_products = await count_products(session)

    amount_of_pages = (total_products + per_page - 1) // per_page

    keyboard = get_product_slider(
        products=products,
        page=page,
        amount_of_pages=amount_of_pages,
        objects_per_page=per_page,
    )

    await callback_query.message.edit_text(
        text=f"Выберите продукт в категории:",
        reply_markup=keyboard,
    )


@category_slider.callback_query(MyCallback.filter(F.action.startswith("add_to_cart_")))
async def add_to_cart_handler(callback_query: CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split("_")[-1])

    await state.update_data(product_id=product_id)

    message = await callback_query.message.edit_text(
        "Введите количество товара, которое вы хотите добавить в корзину:"
    )
    await state.update_data(last_message_id=message.message_id)
    await state.set_state(CartState.waiting_for_quantity)


@category_slider.message(StateFilter(CartState.waiting_for_quantity))
async def handle_quantity_input(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    amount_str = message.text.strip()

    user_data = await state.get_data()
    product_id = user_data.get("product_id")
    last_message_id = user_data.get("last_message_id")

    if last_message_id:
        await bot.delete_message(chat_id=user_id, message_id=last_message_id)

    if not amount_str.isdigit() or int(amount_str) <= 0:
        response_message = await message.reply(
            "Пожалуйста, введите корректное количество (целое число больше 0)."
        )
        await state.update_data(last_message_id=response_message.message_id)
        return

    amount = int(amount_str)

    async with async_session() as session:
        product = await get_product_by_id(session, product_id)

        if not product:
            response_message = await message.reply(
                "Продукт не найден. Попробуйте снова."
            )
            await state.update_data(last_message_id=response_message.message_id)
            await state.clear()
            return

        cart_item = CartCreateSchema(
            user_id=user_id, product_id=product_id, amount=amount
        )
        try:
            await create_cart_item(session, cart_item)
        except InsufficientStockException:
            response_message = await message.reply(
                f"Извините, в наличии только {product.amount} единиц этого товара."
            )
            await state.update_data(last_message_id=response_message.message_id)
            return

    confirmation_message = await bot.send_message(
        chat_id=user_id,
        text=(
            f"Товар '{product.name}' добавлен в вашу корзину. "
            f"Количество: {amount}, Общая стоимость: {amount * product.cost}₽. "
            "Перейдите в корзину, чтобы продолжить."
        ),
        reply_markup=get_back_to_main_menu_keyboard(),
    )

    await state.update_data(last_message_id=confirmation_message.message_id)

    await state.clear()
