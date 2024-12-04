import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import db.models as m
from schemas.faq import FAQSchema, FAQCreateSchema


async def get_faq_by_id(session: AsyncSession, faq_id: int) -> Optional[FAQSchema]:
    q = sa.select(m.FAQ.__table__).where(m.FAQ.id == faq_id)
    entity = (await session.execute(q)).mappings().first()

    if entity:
        return FAQSchema(**entity)


async def get_all_faqs(
    session: AsyncSession, page: int, per_page: int
) -> Optional[List[FAQSchema]]:
    q = sa.select(m.FAQ.__table__).offset(per_page * page).limit(per_page)
    entities = (await session.execute(q)).mappings().all()

    if entities:
        return [FAQSchema(**entity) for entity in entities]


async def count_faqs(session: AsyncSession) -> int:
    q = sa.select(sa.func.count(m.FAQ.id))
    return (await session.execute(q)).scalar()


async def create_faq(session: AsyncSession, schema: FAQCreateSchema):
    q = sa.select(m.FAQ.title).where(m.FAQ.title == schema.title)
    faq_exists = (await session.execute(q)).scalar()

    if faq_exists:
        raise ValueError(f"FAQ with title '{schema.title}' already exists.")

    q = sa.insert(m.FAQ).values(title=schema.title, text=schema.text)
    await session.execute(q)


async def delete_faq(session: AsyncSession, faq_id: int):
    q = sa.select(m.FAQ.id).where(m.FAQ.id == faq_id)
    faq_exists = (await session.execute(q)).scalar()

    if not faq_exists:
        raise ValueError(f"FAQ with ID {faq_id} not found.")

    q = sa.delete(m.FAQ).where(m.FAQ.id == faq_id)
    await session.execute(q)
