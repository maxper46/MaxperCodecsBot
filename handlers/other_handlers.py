from aiogram import Router
from aiogram.types import Message


router = Router()


@router.message()
async def send_echo(message: Message):
    await message.answer(f'Это эхо! {message.text}\n'
                         f'Вероятно, вы ввели неправильную команду или номер статьи.\n'
                         f'А например, в КоАП РФ все номера статей содержат точку (1.1)')
