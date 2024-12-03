import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import db.models as m
from schemas.category import CategorySchema, CategoryUpdateSchema


async def get_category_by_id(
    session: AsyncSession, category_id: int
) -> Optional[CategorySchema]:
    q = sa.select(m.Category.__table__).where(m.Category.id == category_id)
    entity = (await session.execute(q)).mappings().first()

    if entity:
        return CategorySchema(**entity)


async def get_all_categories(
    session: AsyncSession, page: int = 0, per_page: int = 10
) -> Optional[List[CategorySchema]]:
    q = sa.select(m.Category.__table__).offset(page * per_page).limit(per_page)
    entities = (await session.execute(q)).mappings().all()

    if entities:
        return [CategorySchema(**entity) for entity in entities]


async def count_categories(session: AsyncSession) -> int:
    q = sa.select(sa.func.count(m.Category.id))
    return (await session.execute(q)).scalar()


async def create_category(session: AsyncSession, name: str):
    q = sa.select(m.Category.name).where(m.Category.name == name)
    exists = (await session.execute(q)).scalar()

    if exists:
        raise ValueError(f"Category with name {name} already exists.")

    q = sa.insert(m.Category).values({m.Category.name: name})
    await session.execute(q)


async def update_category(session: AsyncSession, schema: CategoryUpdateSchema):
    q = sa.select(m.Category.name).where(m.Category.name == schema.name)
    exists = (await session.execute(q)).scalar()

    if not exists:
        raise ValueError(f"Category with name {schema.name} not found.")

    q = (
        sa.update(m.Category)
        .where(m.Category.name == schema.name)
        .values(
            {
                m.Category.name: schema.name,
                m.Category.products_amount: m.Category.products_amount
                + schema.products_amount,
            }
        )
    )
    await session.execute(q)


async def delete_category(session: AsyncSession, name: str):
    q = sa.select(m.Category.name).where(m.Category.name == name)
    exists = (await session.execute(q)).scalar()

    if not exists:
        raise ValueError(f"Category with name {name} not found.")

    q = sa.delete(m.Category).where(m.Category.name == name)
    await session.execute(q)
