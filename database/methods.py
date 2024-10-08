from sqlalchemy import URL, select, update, insert, exists
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from config import database_args
from database.models import Docs, Users
from files import prepare_dict


class Database:
    def __init__(self):
        self.conn_args = database_args()
        url_object = URL.create("postgresql+asyncpg", username=self.conn_args['user'],
                                password=self.conn_args['password'], host=self.conn_args['host'],
                                port=self.conn_args['port'], database=self.conn_args['dbname'],)
        self.engine = create_async_engine(url_object)
        self.async_session = async_sessionmaker(self.engine)

    async def is_user_exists(self, user_id: int) -> bool:
        async with self.async_session() as session:
            stmt = select(exists().where(Users.user_id == user_id))
            result = await session.execute(stmt)
            return result.scalar()

    async def get_titles_list(self) -> list:
        async with self.async_session() as session:
            stmt = select(Docs.title)
            result = await session.execute(stmt)
            return [i[0] for i in result] if result else []

    async def create_if_not_exists(self, user_id: int, current_doc: int | None, current_art: str,
                                   current_page: int, bookmarks: dict
                                   ) -> None:
        user = Users(user_id=user_id, current_doc=current_doc, current_art=current_art, current_page=current_page,
                     bookmarks=bookmarks)
        async with self.async_session() as session:
            session.add(user)
            await session.commit()

    async def get_current_doc_id(self, user_id: int) -> tuple:
        async with self.async_session() as session:
            stmt = select(Users.current_doc).where(Users.user_id == user_id)
            result = await session.execute(stmt)
            return tuple(result.one())

    async def get_current_info(self, user_id: int) -> tuple:
        async with self.async_session() as session:
            stmt = select(Users.current_doc, Users.current_art, Users.current_page).where(Users.user_id == user_id)
            result = await session.execute(stmt)
            return tuple(result.one())

    async def set_current_doc(self, user_id: int, doc_id: int, art_number: str = '1', page_number: int = 1) -> None:
        async with self.async_session() as session:
            stmt = update(Users).values(current_doc=doc_id, current_art=art_number, current_page=page_number)\
                .where(Users.user_id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def set_current_art(self, user_id: int, art_number: str) -> None:
        async with self.async_session() as session:
            stmt = update(Users).values(current_art=art_number, current_page=1).where(Users.user_id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def set_current_page(self, user_id: int, page_number: int) -> None:
        async with self.async_session() as session:
            stmt = update(Users).values(current_page=page_number).where(Users.user_id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def get_doc_data(self, doc_id: int, key: str) -> str | dict:
        async with self.async_session() as session:
            stmt = select(Docs.content[key]).where(Docs.doc_id == doc_id)
            tmp_result = await session.execute(stmt)
            result = tmp_result.fetchone()
            return result[0]

    async def is_key_exists(self, doc_id: int, key: str) -> bool:
        async with self.async_session() as session:
            stmt = select(Docs.content.op('?')(key)).where(Docs.doc_id == doc_id)
            result = await session.execute(stmt)
            return result.one()[0]

    async def add_bookmark(self, user_id: int, key: str, value: str) -> None:
        bookmark = {key: value}
        async with self.async_session() as session:
            stmt = update(Users).values(bookmarks=Users.bookmarks.op('||')(bookmark)).where(Users.user_id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def get_bookmarks(self, user_id: int) -> dict:
        async with self.async_session() as session:
            stmt = select(Users.bookmarks).where(Users.user_id == user_id)
            result = await session.execute(stmt)
            return result.one()[0]

    async def del_bookmark(self, user_id: int, key: str) -> None:
        dicts = await self.get_bookmarks(user_id)
        del dicts[key]
        async with self.async_session() as session:
            stmt = update(Users).values(bookmarks=dicts).where(Users.user_id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def bookmarks_counter(self, user_id: int) -> int:
        async with self.async_session() as session:
            stmt = select(Users.bookmarks).where(Users.user_id == user_id)
            result = await session.execute(stmt)
            return len(result.one()[0])

    async def is_bookmark_exists(self, user_id: int, key: str) -> bool:
        async with self.async_session() as session:
            stmt = select(Users.bookmarks.op('?')(key)).where(Users.user_id == user_id)
            result = await session.execute(stmt)
            return result.one()[0]


async def is_doc_exists(as_session: async_sessionmaker[AsyncSession], doc_title: str) -> bool:
    async with as_session() as session:
        stmt = select(exists().where(Docs.title == doc_title))
        result = await session.execute(stmt)
        return result.scalar()


async def update_docs_table(as_engine: AsyncEngine, filenames: list) -> None:
    async_session = async_sessionmaker(as_engine)
    async with async_session() as session:
        stmt = select(Docs.title)
        result = await session.execute(stmt)
        titles = [i[0] for i in result] if result else []
        for file_name in filenames:
            if 'pdd_rf' in file_name:
                continue
            doc_content = await prepare_dict(file_name)
            tmp_title = doc_content['doc_title']
            doc_title = tmp_title if '"' not in tmp_title else tmp_title[tmp_title.index('"') + 1:tmp_title.rindex('"')]
            if doc_title in titles:
                stmt = update(Docs).where(Docs.title==doc_title).values(filename=file_name, content=doc_content)
                result = await session.execute(stmt)
            else:
                stmt = insert(Docs).values(title=doc_title, filename=file_name, content=doc_content)
                result = await session.execute(stmt)
        await session.commit()

bot_database = Database()
