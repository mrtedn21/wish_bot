# This file stores models for db
import asyncio

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

engine = create_async_engine('postgresql+asyncpg://@localhost/wish_db', future=True)
Base = declarative_base()


class Wish(Base):
    __tablename__ = 'wish'
    id = Column(Integer, primary_key=True)
    user = Column(String(64))
    text = Column(String(256))


# This part of file needs to create all table
# Therefore it calls only if file execute directly

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
