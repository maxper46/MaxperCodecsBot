from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from database.database import bot_database as db


class IsDelBookmarkCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.endswith('del') and callback.data[:-3].isdigit()


class IsArticleNumberCorrectMessageData(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        current_doc = db.get_current_doc_id(message.from_user.id)
        result = db.is_key_exists(*current_doc, message.text)
        return result
