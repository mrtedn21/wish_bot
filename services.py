# This file store db logic, work with models, etc.
from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.database import PrivateUser
from models.database import Wish
from models.database import async_session


async def create_wish(username: str, text: str, private: bool) -> bool:
    """ If error, function return False """
    async with async_session() as session:
        try:
            await session.execute(
                insert(Wish).values(
                    username=username,
                    text=text,
                    private=private
                )
            )
        except IntegrityError:
            return False
        await session.commit()
    return True


async def get_wishes_by_username(username: str):
    async with async_session() as session:
        result = await session.execute(
            select(Wish.id, Wish.text)
                .where(Wish.username == username)
                .order_by(Wish.text)
        )
        return result.fetchall()


async def delete_wish_by_id(pk: int) -> None:
    async with async_session() as session:
        await session.execute(
            delete(Wish)
                .where(Wish.id == pk)
        )
        await session.commit()


async def create_private_user(username: str, private_username: str) -> None:
    async with async_session() as session:
        await session.execute(
            insert(PrivateUser).values(
                username=username,
                private_username=private_username
            )
        )
        await session.commit()


async def get_private_users(username: str):
    async with async_session() as session:
        result = await session.execute(
            select(PrivateUser.private_username)
                .where(PrivateUser.username == username)
        )
        return result.fetchall()


async def delete_private_user(username: str, private_username: str):
    async with async_session() as session:
        await session.execute(
            delete(PrivateUser)
                .where(PrivateUser.private_username == private_username)
        )
        await session.commit()
