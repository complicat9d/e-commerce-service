import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import db.models as m
from schemas.cart import CartSchema, CartCreateSchema
from schemas.exc import InsufficientStockException
from utils.db.product import get_product_by_id


async def get_cart_by_user_id(
    session: AsyncSession, user_id: int
) -> Optional[List[CartSchema]]:
    q = sa.select(m.Cart.__table__).where(m.Cart.user_id == user_id)
    entities = (await session.execute(q)).mappings().all()

    if entities:
        return [CartSchema(**entity) for entity in entities]


async def get_cart_item(
    session: AsyncSession, user_id: int, product_id: int
) -> Optional[CartSchema]:
    q = sa.select(m.Cart.__table__).where(
        sa.and_(m.Cart.user_id == user_id, m.Cart.product_id == product_id)
    )
    entity = (await session.execute(q)).mappings().first()

    if entity:
        return CartSchema(**entity)


async def create_cart_item(session: AsyncSession, schema: CartCreateSchema):
    product = await get_product_by_id(session, schema.product_id)
    if product.amount - schema.amount < 0:
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
        amount=schema.amount,
        cost=schema.amount * product.cost,
    )
    await session.execute(q)


async def delete_cart_item(session: AsyncSession, user_id: int, product_id: int):
    q = sa.select(m.Cart.id, m.Cart.amount).where(
        sa.and_(m.Cart.user_id == user_id, m.Cart.product_id == product_id)
    )
    cart_item_exists, amount = (await session.execute(q)).all()

    if not cart_item_exists:
        raise ValueError(
            f"Cart item with user_id {user_id} and product_id {product_id} not found."
        )

    q = (
        sa.update(m.Product)
        .values({m.Product.amount: m.Product.amount + amount})
        .where(m.Product.id == product_id)
    )
    await session.execute(q)

    q = sa.delete(m.Cart).where(
        sa.and_(m.Cart.user_id == user_id, m.Cart.product_id == product_id)
    )
    await session.execute(q)


async def count_cart_items(session: AsyncSession, user_id: int) -> int:
    q = sa.select(sa.func.count(m.Cart.id)).where(m.Cart.user_id == user_id)
    return (await session.execute(q)).scalar()
