from sqlalchemy import Integer, Text, BigInteger, String, ForeignKeyConstraint, Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedColumn
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Docs(Base):
    __tablename__ = 'docs'
    doc_id: Mapped[int] = MappedColumn(Integer, Sequence('user_id_seq', start=1), primary_key=True)
    title: Mapped[str] = MappedColumn(Text, nullable=False)
    filename: Mapped[str] = MappedColumn(Text, nullable=False)
    content: Mapped[dict[str, str]] = MappedColumn(JSONB, nullable=False)


class Users(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = MappedColumn(BigInteger, primary_key=True)
    current_doc: Mapped[int] = MappedColumn(Integer, nullable=False)
    current_art: Mapped[str] = MappedColumn(String, nullable=False)
    current_page: Mapped[int] = MappedColumn(Integer, nullable=False)
    bookmarks: Mapped[dict[str, str]] = MappedColumn(JSONB, nullable=False)
    ForeignKeyConstraint([current_doc], [Docs.doc_id])
