# This file store db logic, work with models, etc.
from models.database import Wish
from models.database import async_session
from sqlalchemy import insert


async def create_wish(user, text):
    async with async_session() as session:
        await session.execute(
            insert(Wish).values(user=user, text=text)
        )
        await session.commit()
