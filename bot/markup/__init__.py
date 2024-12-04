from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from typing import List

from schemas.category import CategorySchema
from schemas.product import ProductSchema
from schemas.cart import CartSchema


class MyCallback(CallbackData, prefix="action"):
    action: str


def get_back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=MyCallback(action="back_to_main_menu").pack(),
                )
            ]
        ]
    )


def get_back_to_category(category_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=MyCallback(
                        action="category_{}".format(category_id)
                    ).pack(),
                )
            ]
        ]
    )


def get_product_menu(category_id: int, product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Добавить в корзину",
                    callback_data=MyCallback(
                        action="add_to_cart_{}".format(product_id)
                    ).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=MyCallback(
                        action="category_{}".format(category_id)
                    ).pack(),
                )
            ],
        ]
    )


def get_back_to_catalog() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=MyCallback(action="catalog").pack(),
                )
            ]
        ]
    )


def get_index_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Каталог", callback_data=MyCallback(action="catalog").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Корзина", callback_data=MyCallback(action="cart").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="FAQ", callback_data=MyCallback(action="faq").pack()
                )
            ],
        ],
    )


def get_category_slider(
    categories: List[CategorySchema],
    amount_of_pages: int,
    page: int = 0,
    objects_per_page: int = 5,
) -> InlineKeyboardMarkup:
    keyboard = []

    start_index = page * objects_per_page
    for i, category in enumerate(categories, start=1 + start_index):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{i}. {category.name}",
                    callback_data=MyCallback(action=f"category_{category.id}").pack(),
                )
            ]
        )

    slider = []
    if page > 0:
        slider.append(
            InlineKeyboardButton(
                text="<",
                callback_data=MyCallback(action=f"category_page_{page - 1}").pack(),
            )
        )

    if amount_of_pages > 1:
        slider.append(
            InlineKeyboardButton(
                text="{} / {}".format(page + 1, amount_of_pages),
                callback_data=MyCallback(action=f"category_page_{page + 1}").pack(),
            )
        )

    if page < amount_of_pages - 1:
        slider.append(
            InlineKeyboardButton(
                text=">",
                callback_data=MyCallback(action=f"category_page_{page + 1}").pack(),
            )
        )

    keyboard.append(slider)
    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=MyCallback(action="back_to_main_menu").pack(),
            )
        ]
    )

    return InlineKeyboardMarkup(
        row_width=1, inline_keyboard=[button for button in keyboard]
    )


def get_product_slider(
    products: List[ProductSchema],
    amount_of_pages: int,
    category_id: int,
    page: int = 0,
    objects_per_page: int = 5,
) -> InlineKeyboardMarkup:
    keyboard = []

    start_index = page * objects_per_page
    for i, product in enumerate(products, start=1 + start_index):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{i}. {product.name} - {product.cost}₽",
                    callback_data=MyCallback(action=f"product_{product.id}").pack(),
                )
            ]
        )

    slider = []
    if page > 0:
        slider.append(
            InlineKeyboardButton(
                text="<",
                callback_data=MyCallback(
                    action=f"product_page_{category_id}_{page - 1}"
                ).pack(),
            )
        )

    if amount_of_pages > 1:
        slider.append(
            InlineKeyboardButton(
                text="{} / {}".format(page + 1, amount_of_pages),
                callback_data=MyCallback(
                    action=f"product_page_{category_id}_{page + 1}"
                ).pack(),
            )
        )

    if page < amount_of_pages - 1:
        slider.append(
            InlineKeyboardButton(
                text=">",
                callback_data=MyCallback(
                    action=f"product_page_{category_id}_{page + 1}"
                ).pack(),
            )
        )

    keyboard.append(slider)
    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=MyCallback(action=f"catalog").pack(),
            )
        ]
    )

    return InlineKeyboardMarkup(
        row_width=1, inline_keyboard=[button for button in keyboard]
    )


def get_cart_slider(
    cart_items: List[CartSchema],  # List of items in the cart
    page: int,  # Current page
    total_pages: int,
    per_page: int,
) -> InlineKeyboardMarkup:
    keyboard = []

    # Add cart items to the keyboard
    start_index = page * per_page
    for i, item in enumerate(cart_items, start=1 + start_index):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{i}. {item.product_name} - {item.amount} шт. цена: {item.cost}",
                    callback_data=MyCallback(
                        action=f"cart_item_{item.product_id}"
                    ).pack(),
                )
            ]
        )

    slider = []
    if page > 0:
        slider.append(
            InlineKeyboardButton(
                text="<",
                callback_data=MyCallback(action=f"cart_page_{page - 1}").pack(),
            )
        )
    if total_pages > 1:
        slider.append(
            InlineKeyboardButton(
                text=f"{page + 1} / {total_pages}",
                callback_data=MyCallback(action=f"cart_page_{page}").pack(),
            )
        )

    if page < total_pages - 1:
        slider.append(
            InlineKeyboardButton(
                text=">",
                callback_data=MyCallback(action=f"cart_page_{page + 1}").pack(),
            )
        )

    keyboard.append(slider)

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=MyCallback(action="back_to_main_menu").pack(),
            )
        ]
    )

    return InlineKeyboardMarkup(
        row_width=1, inline_keyboard=[button for button in keyboard]
    )


def get_product_actions(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📍 Указать адрес",
                    callback_data=MyCallback(
                        action=f"cart_address_{product_id}"
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить из корзины",
                    callback_data=MyCallback(action=f"cart_delete_{product_id}").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=MyCallback(action="cart").pack(),
                ),
            ],
        ]
    )


def get_back_to_cart_address(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=MyCallback(action=f"cart_address_{product_id}").pack()
                )
            ]
        ]
    )
