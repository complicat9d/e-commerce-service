import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import db.models as m
from schemas.product import ProductSchema, ProductCreateSchema


async def get_product_by_id(
    session: AsyncSession, product_id: int
) -> Optional[ProductSchema]:
    q = sa.select(m.Product.__table__).where(m.Product.id == product_id)
    entity = (await session.execute(q)).mappings().first()

    if entity:
        return ProductSchema(**entity)


async def get_all_products(session: AsyncSession) -> Optional[List[ProductSchema]]:
    q = sa.select(m.Product.__table__)
    entities = (await session.execute(q)).mappings().all()

    if entities:
        return [ProductSchema(**entity) for entity in entities]


async def get_all_products_by_category(
    session: AsyncSession, category_id: int, page: int = 0, per_page: int = 5
) -> Optional[List[ProductSchema]]:
    q = (
        sa.select(m.Product.__table__)
        .offset(page * per_page)
        .limit(per_page)
        .where(sa.and_(m.Product.category_id == category_id, m.Product.amount > 0))
    )
    entities = (await session.execute(q)).mappings().all()

    if entities:
        return [ProductSchema(**entity) for entity in entities]


async def count_products(session: AsyncSession) -> int:
    q = sa.select(sa.func.count(m.Product.id))
    return (await session.execute(q)).scalar()


async def create_product(session: AsyncSession, schema: ProductCreateSchema):
    q = sa.select(m.Product.name).where(
        sa.and_(
            m.Product.name == schema.name,
            m.Product.category_name == schema.category_name,
        )
    )
    product_exists = (await session.execute(q)).scalar()

    if product_exists:
        raise ValueError(
            f"Product with name {schema.name} already exists in category {schema.category_name}."
        )

    q = sa.insert(m.Product).values(
        category_name=schema.category_name,
        name=schema.name,
        photo=schema.photo,
        description=schema.description,
        cost=schema.cost,
    )
    await session.execute(q)


async def delete_product(session: AsyncSession, product_id: int):
    q = sa.select(m.Product.id).where(m.Product.id == product_id)
    product_exists = (await session.execute(q)).scalar()

    if not product_exists:
        raise ValueError(f"Product with ID {product_id} not found.")

    q = sa.delete(m.Product).where(m.Product.id == product_id)
    await session.execute(q)
