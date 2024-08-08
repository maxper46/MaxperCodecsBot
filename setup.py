#!/usr/bin/env python

import asyncio
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import database_args
from database.models import Base
from files import get_links, load_base_page, load_codecses, BASE_URL
from database.methods import update_docs_table


async def main():
    args = database_args()
    url_object = URL.create("postgresql+asyncpg", username=args['user'],
                            password=args['password'], host=args['host'],
                            port=args['port'], database=args['dbname'],)
    engine = create_async_engine(url_object)
    async_session = async_sessionmaker(engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await load_base_page(BASE_URL)
    links = await get_links()
    file_names = await load_codecses(links)
    await update_docs_table(async_session, file_names, True)
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
