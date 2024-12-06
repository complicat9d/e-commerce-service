import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import false
from typing import List, Optional

import db.models as m
from schemas.cart import CartSchema, CartCreateSchema, CartUpdateSchema
from schemas.exc import InsufficientStockException


async def get_cart_by_user_id(
    session: AsyncSession, user_id: int, page: int = 0, per_page: int = 5
) -> Optional[List[CartSchema]]:
    q = (
        sa.select(m.Cart.__table__)
        .where(sa.and_(m.Cart.user_id == user_id, m.Cart.is_being_delivered == false()))
        .offset(page * per_page)
        .limit(per_page)
    )
    entities = (await session.execute(q)).mappings().all()

    if entities:
        return [CartSchema(**entity) for entity in entities]


async def get_cart_item_by_id(
    session: AsyncSession, cart_id: int
) -> Optional[CartSchema]:
    q = sa.select(m.Cart.__table__).where(m.Cart.id == cart_id)
    entity = (await session.execute(q)).mappings().first()

    if entity:
        return CartSchema(**entity)


async def create_cart_item(session: AsyncSession, schema: CartCreateSchema):
    if schema.product_amount - schema.amount < 0:
        raise InsufficientStockException

    q0 = (
        sa.update(m.Product)
        .values({m.Product.amount: m.Product.amount - schema.amount})
        .where(m.Product.id == schema.product_id)
    )
    await session.execute(q0)

    q = sa.insert(m.Cart).values(
        user_id=schema.user_id,
        product_id=schema.product_id,
        product_name=schema.product_name,
        amount=schema.amount,
        cost=schema.amount * schema.cost,
        is_being_delivered=False,
    )
    await session.execute(q)


async def delete_cart_item_by_id(session: AsyncSession, cart_id: int):
    q = sa.select(m.Cart.user_id, m.Cart.product_id, m.Cart.amount).where(
        m.Cart.id == cart_id
    )
    cart_item_exists, product_id, amount = (await session.execute(q)).all()[0]

    if not cart_item_exists:
        raise ValueError(f"Cart item with id {cart_id} not found.")

    q = (
        sa.update(m.Product)
        .values({m.Product.amount: m.Product.amount + amount})
        .where(m.Product.id == product_id)
    )
    await session.execute(q)

    q = sa.delete(m.Cart).where(m.Cart.id == cart_id)
    await session.execute(q)


async def update_cart_by_id(session: AsyncSession, schema: CartUpdateSchema):
    q = sa.select(m.Cart.id).where(m.Cart.id == schema.id)
    cart_item_exists = (await session.execute(q)).scalar()

    if not cart_item_exists:
        raise ValueError(f"Cart item with id {schema.cart_id} not found.")

    data = {}
    if schema.is_being_delivered is not None:
        data[m.Cart.is_being_delivered] = schema.is_being_delivered
    if schema.address:
        data[m.Cart.address] = schema.address

    q = sa.update(m.Cart).values(data).where(m.Cart.id == schema.id)
    await session.execute(q)


async def count_cart_items(session: AsyncSession, user_id: int) -> int:
    q = sa.select(sa.func.count(m.Cart.user_id)).where(
        sa.and_(m.Cart.user_id == user_id, m.Cart.is_being_delivered == false())
    )
    return (await session.execute(q)).scalar()
