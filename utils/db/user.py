import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import db.models as m
from schemas.user import UserSchema


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[UserSchema]:
    q = sa.select(m.User.__table__).where(m.User.id == user_id)
    entity = (await session.execute(q)).mappings().first()

    if entity:
        return UserSchema(**entity)


async def get_all_users(session: AsyncSession) -> Optional[List[UserSchema]]:
    q = sa.select(m.User.__table__).order_by(m.User.id.asc())
    entities = (await session.execute(q)).mappings().all()

    if entities:
        return [UserSchema(**entity) for entity in entities]


async def create_or_update_user(
    session: AsyncSession,
    chat_id: int,
    first_name: str,
    lang: str,
    last_name: str = None,
    username: str = None,
):
    q = sa.select(m.User.id).where(m.User.id == chat_id)
    exists = (await session.execute(q)).scalar()
    if not exists:
        q = sa.insert(m.User).values(
            {
                m.User.id: chat_id,
                m.User.first_name: first_name,
                m.User.last_name: last_name,
                m.User.username: username,
                m.User.lang: lang,
            }
        )
    else:
        q = sa.update(m.User).values(
            {
                m.User.id: chat_id,
                m.User.first_name: first_name,
                m.User.last_name: last_name,
                m.User.username: username,
                m.User.lang: lang,
            }
        )
    await session.execute(q)
