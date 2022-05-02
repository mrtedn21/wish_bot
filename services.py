# This file store db logic, work with models, etc.
from models.database import Wish
from models.database import async_session
from sqlalchemy import insert
from sqlalchemy import select


async def create_wish(username, text):
    async with async_session() as session:
        await session.execute(
            insert(Wish).values(username=username, text=text)
        )
        await session.commit()


async def get_wishes_by_username(username: str):
    async with async_session() as session:
        result = await session.execute(
            select(Wish.text).where(Wish.username == username)
        )
        wishes = result.fetchall()
        # result of fetchall is, for example:
        # [('iphone',), ('corne',), ('gtx 3070',)]
        # i make this list to:
        # ['iphone', 'corne', 'gtx 3070']
        wishes = [wish[0] for wish in wishes]
        return wishes
