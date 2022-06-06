# This file stores models for db
import asyncio
import os

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

db_user = os.environ['POSTGRES_USER']
db_name = os.environ['POSTGRES_DB']
db_password = os.environ['POSTGRES_PASSWORD']
engine = create_async_engine(
    f'postgresql+asyncpg://{db_user}:{db_password}@db/{db_name}', future=True)
Base = declarative_base()
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Wish(Base):
    __tablename__ = 'wishes'
    id = Column(Integer, primary_key=True)
    username = Column(String(64))
    text = Column(String(256))
    private = Column(Boolean, default=False)


class PrivateUser(Base):
    """ there are usernames in user and private_user.
    'private_user' will see private messages of 'user' """
    __tablename__ = 'private_users'
    username = Column(String(64), primary_key=True)
    private_username = Column(String(64), primary_key=True)


# This part of file needs to create all tables
# Therefore it calls only if file execute directly


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text(
            'CREATE UNIQUE INDEX ix_wishes_username_text '
            'ON wishes(username, text)'
        ))

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
