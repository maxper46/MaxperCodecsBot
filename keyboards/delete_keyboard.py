from aiogram import Bot


async def del_keyboard(message_id: int, chat_id: int, key: int, bot: Bot) -> None:
    if message_id:
        if key:
            await bot.delete_message(message_id=message_id, chat_id=chat_id)
        else:
            await bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id)
