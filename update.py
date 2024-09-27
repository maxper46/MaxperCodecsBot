#!/usr/bin/env python

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import URL
from config import database_args
from files import get_links, load_base_page, load_codecses, BASE_URL
from database.methods import update_docs_table


async def main():
    args = database_args()
    await load_base_page(BASE_URL)
    links = await get_links()
    file_names = await load_codecses(links)
    url_object = URL.create("postgresql+asyncpg", username=args['user'],
                        password=args['password'], host=args['host'],
                        port=args['port'], database=args['dbname'],)
    engine = create_async_engine(url_object)
    await update_docs_table(engine, file_names)
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
